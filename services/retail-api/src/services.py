from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import httpx

import src.models as models
import src.schemas as schemas
import src.external_services as external_services
from src.external_services import InventoryService, ExternalServiceError

logger = logging.getLogger(__name__)


class StoreService:
    def __init__(self, db: Session):
        self.db = db

    def get_stores(self, actif: Optional[bool] = None) -> List[models.Store]:
        """Récupérer la liste des magasins avec filtre optionnel"""
        query = self.db.query(models.Store)

        if actif is not None:
            query = query.filter(models.Store.actif == actif)

        return query.order_by(models.Store.nom).all()

    def create_store(self, store: schemas.StoreCreate) -> models.Store:
        """Créer un nouveau magasin"""
        db_store = models.Store(**store.dict())
        self.db.add(db_store)
        self.db.commit()
        self.db.refresh(db_store)
        logger.info(f"✅ Store created: {db_store.nom}")
        return db_store

    def get_store(self, store_id: int) -> Optional[models.Store]:
        """Récupérer un magasin par son ID"""
        return self.db.query(models.Store).filter(models.Store.id == store_id).first()

    def update_store(
        self, store_id: int, store_update: schemas.StoreUpdate
    ) -> Optional[models.Store]:
        """Mettre à jour un magasin"""
        db_store = self.get_store(store_id)
        if not db_store:
            return None

        update_data = store_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_store, field, value)

        self.db.commit()
        self.db.refresh(db_store)
        logger.info(f"✅ Store updated: {db_store.nom}")
        return db_store

    def delete_store(self, store_id: int) -> bool:
        """Supprimer un magasin (désactivation logique)"""
        db_store = self.get_store(store_id)
        if not db_store:
            return False

        db_store.actif = False
        self.db.commit()
        logger.info(f"✅ Store deactivated: {db_store.nom}")
        return True

    def get_store_details(self, store_id: int) -> Optional[schemas.StoreWithDetails]:
        """Obtenir les détails complets d'un magasin"""
        store = self.get_store(store_id)
        if not store:
            return None

        # Calculer les statistiques
        sales_stats = (
            self.db.query(
                func.count(models.Sale.id).label("nombre_transactions"),
                func.coalesce(func.sum(models.Sale.total), 0).label("total_sales"),
            )
            .filter(models.Sale.store_id == store_id)
            .first()
        )

        # Créer l'objet de réponse
        store_details = schemas.StoreWithDetails(
            id=store.id,
            nom=store.nom,
            adresse=store.adresse,
            telephone=store.telephone,
            email=store.email,
            actif=store.actif,
            date_creation=store.date_creation,
            cash_registers=store.cash_registers,
            total_sales=sales_stats.total_sales or 0.0,
            nombre_transactions=sales_stats.nombre_transactions or 0,
        )

        return store_details

    def get_store_performance(
        self, store_id: int
    ) -> Optional[schemas.StorePerformance]:
        """Obtenir les performances d'un magasin"""
        store = self.get_store(store_id)
        if not store:
            return None

        # Calculer les statistiques
        sales_stats = (
            self.db.query(
                func.count(models.Sale.id).label("nombre_transactions"),
                func.coalesce(func.sum(models.Sale.total), 0).label("total_ventes"),
                func.coalesce(func.avg(models.Sale.total), 0).label("panier_moyen"),
                func.max(models.Sale.date_vente).label("derniere_vente"),
            )
            .filter(models.Sale.store_id == store_id)
            .first()
        )

        return schemas.StorePerformance(
            store=store,
            total_ventes=sales_stats.total_ventes or 0.0,
            nombre_transactions=sales_stats.nombre_transactions or 0,
            panier_moyen=sales_stats.panier_moyen or 0.0,
            derniere_vente=sales_stats.derniere_vente,
        )


class CashRegisterService:
    def __init__(self, db: Session):
        self.db = db

    def get_cash_registers(
        self, store_id: Optional[int] = None, actif: Optional[bool] = None
    ) -> List[models.CashRegister]:
        """Récupérer la liste des caisses enregistreuses avec filtres"""
        query = self.db.query(models.CashRegister)

        if store_id is not None:
            query = query.filter(models.CashRegister.store_id == store_id)

        if actif is not None:
            query = query.filter(models.CashRegister.actif == actif)

        return query.order_by(
            models.CashRegister.store_id, models.CashRegister.numero
        ).all()

    def create_cash_register(
        self, cash_register: schemas.CashRegisterCreate
    ) -> models.CashRegister:
        """Créer une nouvelle caisse enregistreuse"""
        db_cash_register = models.CashRegister(**cash_register.dict())
        self.db.add(db_cash_register)
        self.db.commit()
        self.db.refresh(db_cash_register)
        logger.info(f"✅ Cash register created: {db_cash_register.nom}")
        return db_cash_register

    def get_cash_register(self, cash_register_id: int) -> Optional[models.CashRegister]:
        """Récupérer une caisse enregistreuse par son ID"""
        return (
            self.db.query(models.CashRegister)
            .filter(models.CashRegister.id == cash_register_id)
            .first()
        )

    def update_cash_register(
        self, cash_register_id: int, cash_register_update: schemas.CashRegisterUpdate
    ) -> Optional[models.CashRegister]:
        """Mettre à jour une caisse enregistreuse"""
        db_cash_register = self.get_cash_register(cash_register_id)
        if not db_cash_register:
            return None

        update_data = cash_register_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_cash_register, field, value)

        self.db.commit()
        self.db.refresh(db_cash_register)
        logger.info(f"✅ Cash register updated: {db_cash_register.nom}")
        return db_cash_register

    def delete_cash_register(self, cash_register_id: int) -> bool:
        """Supprimer une caisse enregistreuse (désactivation logique)"""
        db_cash_register = self.get_cash_register(cash_register_id)
        if not db_cash_register:
            return False

        db_cash_register.actif = False
        self.db.commit()
        logger.info(f"✅ Cash register deactivated: {db_cash_register.nom}")
        return True


class SaleService:
    def __init__(self, db: Session):
        self.db = db

    def get_sales(
        self,
        store_id: Optional[int] = None,
        cash_register_id: Optional[int] = None,
        date_debut: Optional[str] = None,
        date_fin: Optional[str] = None,
    ) -> List[models.Sale]:
        """Récupérer la liste des ventes avec filtres"""
        query = self.db.query(models.Sale)

        if store_id is not None:
            query = query.filter(models.Sale.store_id == store_id)

        if cash_register_id is not None:
            query = query.filter(models.Sale.cash_register_id == cash_register_id)

        if date_debut:
            query = query.filter(models.Sale.date_vente >= date_debut)

        if date_fin:
            query = query.filter(models.Sale.date_vente <= date_fin)

        return query.order_by(desc(models.Sale.date_vente)).all()

    async def create_sale(self, sale: schemas.SaleCreate) -> models.Sale:
        """Créer une nouvelle vente"""
        # Extraire les lignes de vente
        sale_data = sale.dict()
        lines = sale_data.pop("lines", [])
        
        # Calculer le total
        total = sum(line["quantite"] * line["prix_unitaire"] for line in lines)
        
        # Créer la vente
        db_sale = models.Sale(**sale_data, total=total)
        self.db.add(db_sale)
        self.db.commit()
        self.db.refresh(db_sale)
        
        # Créer les lignes de vente
        for line in lines:
            db_line = models.SaleLine(
                sale_id=db_sale.id,
                product_id=line["product_id"],
                quantite=line["quantite"],
                prix_unitaire=line["prix_unitaire"],
                sous_total=line["quantite"] * line["prix_unitaire"]
            )
            self.db.add(db_line)
        
        self.db.commit()
        self.db.refresh(db_sale)
        
        # Mettre à jour le stock via inventory-api
        try:
            for line in lines:
                await InventoryService.reduce_stock(
                    line["product_id"], 
                    line["quantite"], 
                    "vente_retail", 
                    f"sale_{db_sale.id}"
                )
            logger.info(f"✅ Stock updated for sale {db_sale.id}")
        except Exception as e:
            logger.error(f"❌ Error updating stock for sale {db_sale.id}: {e}")
        
        logger.info(f"✅ Sale created: {db_sale.id} with {len(lines)} lines")
        return db_sale



    def get_sale(self, sale_id: int) -> Optional[models.Sale]:
        """Récupérer une vente par son ID"""
        return self.db.query(models.Sale).filter(models.Sale.id == sale_id).first()

    def update_sale(
        self, sale_id: int, sale_update: schemas.SaleUpdate
    ) -> Optional[models.Sale]:
        """Mettre à jour une vente"""
        db_sale = self.get_sale(sale_id)
        if not db_sale:
            return None

        update_data = sale_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_sale, field, value)

        self.db.commit()
        self.db.refresh(db_sale)
        logger.info(f"✅ Sale updated: {db_sale.id}")
        return db_sale

    def delete_sale(self, sale_id: int) -> bool:
        """Supprimer une vente (annulation logique)"""
        db_sale = self.get_sale(sale_id)
        if not db_sale:
            return False

        db_sale.statut = "annulee"
        self.db.commit()
        logger.info(f"✅ Sale cancelled: {db_sale.id}")
        return True

    def get_sale_lines(self, sale_id: int) -> List[models.SaleLine]:
        """Récupérer les lignes d'une vente"""
        return (
            self.db.query(models.SaleLine)
            .filter(models.SaleLine.sale_id == sale_id)
            .all()
        )

    def get_sales_summary(
        self,
        store_id: Optional[int] = None,
        date_debut: Optional[str] = None,
        date_fin: Optional[str] = None,
    ) -> schemas.RetailSummary:
        """Obtenir un résumé des ventes"""
        query = self.db.query(models.Sale)

        if store_id is not None:
            query = query.filter(models.Sale.store_id == store_id)

        if date_debut:
            query = query.filter(models.Sale.date_vente >= date_debut)

        if date_fin:
            query = query.filter(models.Sale.date_vente <= date_fin)

        # Calculer les statistiques
        stats = query.with_entities(
            func.count(models.Sale.id).label("nombre_ventes"),
            func.coalesce(func.sum(models.Sale.total), 0).label("total_ventes"),
            func.coalesce(func.avg(models.Sale.total), 0).label("panier_moyen"),
        ).first()

        return schemas.RetailSummary(
            nombre_ventes=stats.nombre_ventes or 0,
            total_ventes=float(stats.total_ventes or 0),
            panier_moyen=float(stats.panier_moyen or 0),
        )
