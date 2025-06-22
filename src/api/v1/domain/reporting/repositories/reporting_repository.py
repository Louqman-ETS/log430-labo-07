from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from ..entities.report import GlobalSummary, StorePerformance, TopProduct


class ReportingRepositoryInterface(ABC):
    """Abstract interface for Reporting Repository"""

    @abstractmethod
    def get_global_summary(self) -> GlobalSummary:
        pass

    @abstractmethod
    def get_store_performances(self) -> List[StorePerformance]:
        pass

    @abstractmethod
    def get_top_products(self, limit: int = 10) -> List[TopProduct]:
        pass


class ReportingRepository(ReportingRepositoryInterface):
    """Concrete implementation of Reporting Repository"""

    def __init__(self, db: Session):
        self.db = db

    def get_global_summary(self) -> GlobalSummary:
        """Get global summary from sales data"""
        from src.app.models.models import Vente, LigneVente

        # Calculate total revenue and sales count
        result = (
            self.db.query(
                func.coalesce(
                    func.sum(LigneVente.quantite * LigneVente.prix_unitaire), 0
                ).label("total_revenue"),
                func.count(func.distinct(Vente.id)).label("total_sales_count"),
            )
            .join(Vente, LigneVente.vente_id == Vente.id)
            .first()
        )

        total_revenue = (
            Decimal(str(result.total_revenue))
            if result.total_revenue is not None
            else Decimal("0.00")
        )
        total_sales_count = result.total_sales_count or 0

        return GlobalSummary.calculate_from_data(total_revenue, total_sales_count)

    def get_store_performances(self) -> List[StorePerformance]:
        """Get performance metrics for all stores"""
        from src.app.models.models import Magasin, Vente, LigneVente

        from src.app.models.models import Caisse

        results = (
            self.db.query(
                Magasin.id,
                Magasin.nom,
                func.count(func.distinct(Vente.id)).label("sales_count"),
                func.coalesce(
                    func.sum(LigneVente.quantite * LigneVente.prix_unitaire), 0
                ).label("revenue"),
            )
            .join(Caisse, Magasin.id == Caisse.magasin_id, isouter=True)
            .join(Vente, Caisse.id == Vente.caisse_id, isouter=True)
            .join(LigneVente, Vente.id == LigneVente.vente_id, isouter=True)
            .group_by(Magasin.id, Magasin.nom)
            .all()
        )

        performances = []
        for result in results:
            revenue = (
                Decimal(str(result.revenue))
                if result.revenue is not None
                else Decimal("0.00")
            )
            sales_count = result.sales_count or 0

            performance = StorePerformance.calculate_from_data(
                store_id=result.id,
                store_name=result.nom,
                sales_count=sales_count,
                revenue=revenue,
            )
            performances.append(performance)

        return performances

    def get_top_products(self, limit: int = 10) -> List[TopProduct]:
        """Get top performing products"""
        from src.app.models.models import Produit, LigneVente, Vente

        results = (
            self.db.query(
                Produit.code,
                Produit.nom,
                func.coalesce(func.sum(LigneVente.quantite), 0).label(
                    "total_quantity_sold"
                ),
                func.coalesce(
                    func.sum(LigneVente.quantite * LigneVente.prix_unitaire), 0
                ).label("total_revenue"),
                func.count(func.distinct(Vente.id)).label("total_orders"),
            )
            .join(LigneVente, Produit.id == LigneVente.produit_id, isouter=True)
            .join(Vente, LigneVente.vente_id == Vente.id, isouter=True)
            .group_by(Produit.id, Produit.code, Produit.nom)
            .order_by(func.sum(LigneVente.quantite * LigneVente.prix_unitaire).desc())
            .limit(limit)
            .all()
        )

        top_products = []
        for result in results:
            total_revenue = (
                Decimal(str(result.total_revenue))
                if result.total_revenue is not None
                else Decimal("0.00")
            )
            total_quantity_sold = result.total_quantity_sold or 0
            total_orders = result.total_orders or 0

            top_product = TopProduct(
                product_code=result.code,
                product_name=result.nom,
                total_quantity_sold=total_quantity_sold,
                total_revenue=total_revenue,
                total_orders=total_orders,
            )
            top_products.append(top_product)

        return top_products
