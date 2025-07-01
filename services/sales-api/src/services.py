from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from . import models, schemas
from .external_services import ExternalServiceClient
import logging

logger = logging.getLogger(__name__)

class SaleService:
    def __init__(self, db: Session):
        self.db = db
        self.external_client = ExternalServiceClient()
    
    async def create_sale(self, sale_data: schemas.SaleCreate) -> schemas.SaleResponse:
        """Crée une nouvelle vente avec validation inter-service"""
        
        # Extraire les IDs des produits pour validation
        product_ids = [line.product_id for line in sale_data.sale_lines]
        
        # Valider toutes les données via les APIs externes
        validation = await self.external_client.validate_sale_data(
            sale_data.store_id, 
            sale_data.cash_register_id, 
            product_ids
        )
        
        if not validation["valid"]:
            raise ValueError(f"Validation failed: {', '.join(validation['errors'])}")
        
        # Calculer le total de la vente
        total = 0.0
        sale_lines_data = []
        
        for line in sale_data.sale_lines:
            product = validation["products"][line.product_id]
            sous_total = line.quantite * line.prix_unitaire
            total += sous_total
            
            sale_lines_data.append({
                "product_id": line.product_id,
                "quantite": line.quantite,
                "prix_unitaire": line.prix_unitaire,
                "sous_total": sous_total
            })
        
        # Créer la vente
        db_sale = models.Sale(
            store_id=sale_data.store_id,
            cash_register_id=sale_data.cash_register_id,
            notes=sale_data.notes,
            total=total
        )
        
        self.db.add(db_sale)
        self.db.flush()  # Pour obtenir l'ID
        
        # Créer les lignes de vente
        for line_data in sale_lines_data:
            db_sale_line = models.SaleLine(
                sale_id=db_sale.id,
                **line_data
            )
            self.db.add(db_sale_line)
        
        # Réduire les stocks via l'API Stock
        for line in sale_data.sale_lines:
            success = await self.external_client.reduce_product_stock(
                line.product_id, 
                line.quantite
            )
            if not success:
                logger.warning(f"Failed to reduce stock for product {line.product_id}")
        
        self.db.commit()
        self.db.refresh(db_sale)
        
        return schemas.SaleResponse.model_validate(db_sale)
    
    def get_sales(self, skip: int = 0, limit: int = 100) -> List[schemas.SaleResponse]:
        """Récupère la liste des ventes"""
        sales = self.db.query(models.Sale).offset(skip).limit(limit).all()
        return [schemas.SaleResponse.model_validate(sale) for sale in sales]
    
    def get_sale(self, sale_id: int) -> Optional[schemas.SaleResponse]:
        """Récupère une vente par ID"""
        sale = self.db.query(models.Sale).filter(models.Sale.id == sale_id).first()
        if sale:
            return schemas.SaleResponse.model_validate(sale)
        return None
    
    def get_sales_stats(self) -> schemas.SalesStats:
        """Calcule les statistiques des ventes"""
        stats = self.db.query(
            func.count(models.Sale.id).label("total_sales"),
            func.coalesce(func.sum(models.Sale.total), 0).label("total_revenue"),
            func.coalesce(func.avg(models.Sale.total), 0).label("average_sale_amount")
        ).first()
        
        return schemas.SalesStats(
            total_sales=stats.total_sales or 0,
            total_revenue=float(stats.total_revenue or 0),
            average_sale_amount=float(stats.average_sale_amount or 0)
        )
    
    def get_sales_by_store(self, store_id: int) -> List[schemas.SaleResponse]:
        """Récupère les ventes d'un magasin spécifique"""
        sales = self.db.query(models.Sale).filter(models.Sale.store_id == store_id).all()
        return [schemas.SaleResponse.model_validate(sale) for sale in sales]
    
    def get_sales_by_product(self, product_id: int) -> List[Dict[str, Any]]:
        """Récupère les ventes contenant un produit spécifique"""
        sales_with_product = self.db.query(models.Sale)\
            .join(models.SaleLine)\
            .filter(models.SaleLine.product_id == product_id)\
            .all()
        
        return [schemas.SaleResponse.model_validate(sale) for sale in sales_with_product] 