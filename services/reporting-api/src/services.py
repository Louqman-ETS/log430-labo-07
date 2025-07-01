from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
import math
from datetime import datetime, date

from .models import Sale, SaleLine, StoreStock, CentralStock, RestockingRequest
from .schemas import (
    SaleCreate, SaleUpdate, StoreStockCreate, StoreStockUpdate,
    CentralStockCreate, CentralStockUpdate, RestockingRequestCreate, RestockingRequestUpdate,
    GlobalSummaryResponse, StorePerformanceResponse, TopProductResponse
)
from .external_services import external_client


class SaleService:
    def __init__(self, db: Session):
        self.db = db

    def get_sale(self, sale_id: int) -> Optional[Sale]:
        return self.db.query(Sale).filter(Sale.id == sale_id).first()

    def get_sales(self, skip: int = 0, limit: int = 100) -> List[Sale]:
        return self.db.query(Sale).offset(skip).limit(limit).all()

    async def create_sale(self, sale: SaleCreate) -> Sale:
        # Validate store and cash register exist via API
        store = await external_client.get_store(sale.store_id)
        if not store:
            raise ValueError(f"Store with id {sale.store_id} not found")
        
        cash_register = await external_client.get_cash_register(sale.cash_register_id)
        if not cash_register:
            raise ValueError(f"Cash register with id {sale.cash_register_id} not found")
        
        # Calculate total amount from lines
        total_amount = 0.0
        for line in sale.lines:
            # Validate product exists via API
            product = await external_client.get_product(line.product_id)
            if not product:
                raise ValueError(f"Product with id {line.product_id} not found")
            
            total_amount += line.prix_unitaire * line.quantite
        
        # Create sale
        db_sale = Sale(
            montant_total=total_amount,
            store_id=sale.store_id,
            cash_register_id=sale.cash_register_id
        )
        self.db.add(db_sale)
        self.db.commit()
        self.db.refresh(db_sale)
        
        # Create sale lines
        for line in sale.lines:
            db_line = SaleLine(
                quantite=line.quantite,
                prix_unitaire=line.prix_unitaire,
                product_id=line.product_id,
                sale_id=db_sale.id
            )
            self.db.add(db_line)
            
            # Reduce product stock via Products API
            await external_client.reduce_product_stock(line.product_id, line.quantite)
        
        self.db.commit()
        return db_sale

    def get_sales_by_store(self, store_id: int) -> List[Sale]:
        return self.db.query(Sale).filter(Sale.store_id == store_id).all()

    def get_sales_by_date_range(self, start_date: date, end_date: date) -> List[Sale]:
        return self.db.query(Sale).filter(
            and_(
                Sale.date_heure >= start_date,
                Sale.date_heure <= end_date
            )
        ).all()


class ReportingService:
    def __init__(self, db: Session):
        self.db = db

    async def get_global_summary(self) -> GlobalSummaryResponse:
        """Get global business summary using data from all services"""
        # Get data from local sales
        total_sales = self.db.query(Sale).count()
        total_revenue = self.db.query(func.sum(Sale.montant_total)).scalar() or 0.0
        average_sale_amount = total_revenue / total_sales if total_sales > 0 else 0.0
        
        # Get data from external services
        products = await external_client.get_products(page=1, size=1000)
        stores = await external_client.get_stores(page=1, size=1000)
        
        return GlobalSummaryResponse(
            total_sales=total_sales,
            total_revenue=float(total_revenue),
            total_products=len(products),
            total_stores=len(stores),
            average_sale_amount=float(average_sale_amount)
        )

    async def get_store_performances(self) -> List[StorePerformanceResponse]:
        """Get performance metrics for all stores"""
        # Get sales data grouped by store
        store_sales = self.db.query(
            Sale.store_id,
            func.count(Sale.id).label('sales_count'),
            func.sum(Sale.montant_total).label('revenue'),
            func.avg(Sale.montant_total).label('avg_amount')
        ).group_by(Sale.store_id).all()
        
        # Get store information from external service
        stores = await external_client.get_stores(page=1, size=1000)
        stores_dict = {store['id']: store for store in stores}
        
        performances = []
        for store_sale in store_sales:
            store_info = stores_dict.get(store_sale.store_id, {})
            
            # Calculate performance rating
            revenue = float(store_sale.revenue or 0)
            if revenue > 10000:
                rating = "Excellent"
            elif revenue > 5000:
                rating = "Good"
            elif revenue > 2000:
                rating = "Average"
            else:
                rating = "Below Average"
            
            performances.append(StorePerformanceResponse(
                store_id=store_sale.store_id,
                store_name=store_info.get('nom', f'Store {store_sale.store_id}'),
                sales_count=store_sale.sales_count,
                revenue=revenue,
                average_sale_amount=float(store_sale.avg_amount or 0),
                performance_rating=rating
            ))
        
        return sorted(performances, key=lambda x: x.revenue, reverse=True)

    async def get_top_products(self, limit: int = 10) -> List[TopProductResponse]:
        """Get top performing products"""
        # Get product sales data
        product_sales = self.db.query(
            SaleLine.product_id,
            func.sum(SaleLine.quantite).label('total_quantity'),
            func.sum(SaleLine.quantite * SaleLine.prix_unitaire).label('total_revenue'),
            func.count(SaleLine.id).label('sales_count')
        ).group_by(SaleLine.product_id).order_by(
            func.sum(SaleLine.quantite * SaleLine.prix_unitaire).desc()
        ).limit(limit).all()
        
        # Get product information from external service
        top_products = []
        for product_sale in product_sales:
            product_info = await external_client.get_product(product_sale.product_id)
            
            top_products.append(TopProductResponse(
                product_id=product_sale.product_id,
                product_name=product_info.get('nom', f'Product {product_sale.product_id}') if product_info else f'Product {product_sale.product_id}',
                product_code=product_info.get('code', '') if product_info else '',
                total_quantity_sold=product_sale.total_quantity,
                total_revenue=float(product_sale.total_revenue),
                sales_count=product_sale.sales_count
            ))
        
        return top_products

    async def get_store_performance(self, store_id: int) -> Optional[StorePerformanceResponse]:
        """Get performance for a specific store"""
        # Verify store exists
        store_info = await external_client.get_store(store_id)
        if not store_info:
            return None
        
        # Get sales data for this store
        store_sales = self.db.query(
            func.count(Sale.id).label('sales_count'),
            func.sum(Sale.montant_total).label('revenue'),
            func.avg(Sale.montant_total).label('avg_amount')
        ).filter(Sale.store_id == store_id).first()
        
        if not store_sales or store_sales.sales_count == 0:
            return StorePerformanceResponse(
                store_id=store_id,
                store_name=store_info.get('nom', f'Store {store_id}'),
                sales_count=0,
                revenue=0.0,
                average_sale_amount=0.0,
                performance_rating="No Sales"
            )
        
        # Calculate performance rating
        revenue = float(store_sales.revenue or 0)
        if revenue > 10000:
            rating = "Excellent"
        elif revenue > 5000:
            rating = "Good"
        elif revenue > 2000:
            rating = "Average"
        else:
            rating = "Below Average"
        
        return StorePerformanceResponse(
            store_id=store_id,
            store_name=store_info.get('nom', f'Store {store_id}'),
            sales_count=store_sales.sales_count,
            revenue=revenue,
            average_sale_amount=float(store_sales.avg_amount or 0),
            performance_rating=rating
        )


class StockService:
    def __init__(self, db: Session):
        self.db = db

    def get_store_stock(self, store_id: int, product_id: int) -> Optional[StoreStock]:
        return self.db.query(StoreStock).filter(
            StoreStock.store_id == store_id,
            StoreStock.product_id == product_id
        ).first()

    def get_store_stocks(self, store_id: int) -> List[StoreStock]:
        return self.db.query(StoreStock).filter(StoreStock.store_id == store_id).all()

    async def create_store_stock(self, stock: StoreStockCreate) -> StoreStock:
        # Validate store and product exist via API
        store = await external_client.get_store(stock.store_id)
        if not store:
            raise ValueError(f"Store with id {stock.store_id} not found")
        
        product = await external_client.get_product(stock.product_id)
        if not product:
            raise ValueError(f"Product with id {stock.product_id} not found")
        
        # Check if stock already exists
        existing = self.get_store_stock(stock.store_id, stock.product_id)
        if existing:
            raise ValueError(f"Stock already exists for store {stock.store_id} and product {stock.product_id}")
        
        db_stock = StoreStock(**stock.dict())
        self.db.add(db_stock)
        self.db.commit()
        self.db.refresh(db_stock)
        return db_stock

    def get_central_stock(self, product_id: int) -> Optional[CentralStock]:
        return self.db.query(CentralStock).filter(CentralStock.product_id == product_id).first()

    def get_central_stocks(self) -> List[CentralStock]:
        return self.db.query(CentralStock).all()

    async def create_central_stock(self, stock: CentralStockCreate) -> CentralStock:
        # Validate product exists via API
        product = await external_client.get_product(stock.product_id)
        if not product:
            raise ValueError(f"Product with id {stock.product_id} not found")
        
        # Check if stock already exists
        existing = self.get_central_stock(stock.product_id)
        if existing:
            raise ValueError(f"Central stock already exists for product {stock.product_id}")
        
        db_stock = CentralStock(**stock.dict())
        self.db.add(db_stock)
        self.db.commit()
        self.db.refresh(db_stock)
        return db_stock


class RestockingService:
    def __init__(self, db: Session):
        self.db = db

    def get_restocking_request(self, request_id: int) -> Optional[RestockingRequest]:
        return self.db.query(RestockingRequest).filter(RestockingRequest.id == request_id).first()

    def get_restocking_requests(self) -> List[RestockingRequest]:
        return self.db.query(RestockingRequest).all()

    def get_restocking_requests_by_store(self, store_id: int) -> List[RestockingRequest]:
        return self.db.query(RestockingRequest).filter(RestockingRequest.store_id == store_id).all()

    async def create_restocking_request(self, request: RestockingRequestCreate) -> RestockingRequest:
        # Validate store and product exist via API
        store = await external_client.get_store(request.store_id)
        if not store:
            raise ValueError(f"Store with id {request.store_id} not found")
        
        product = await external_client.get_product(request.product_id)
        if not product:
            raise ValueError(f"Product with id {request.product_id} not found")
        
        db_request = RestockingRequest(**request.dict())
        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)
        return db_request

    def update_restocking_request_status(self, request_id: int, status: str) -> Optional[RestockingRequest]:
        db_request = self.get_restocking_request(request_id)
        if not db_request:
            return None
        
        valid_statuses = ["en_attente", "validee", "livree"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        db_request.statut = status
        self.db.commit()
        self.db.refresh(db_request)
        return db_request 