from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Tuple
from datetime import datetime
import logging

import src.models as models
import src.schemas as schemas

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_products(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        actif: Optional[bool] = None,
    ) -> Tuple[List[models.Product], int]:
        """Récupérer les produits avec filtres et pagination"""
        query = self.db.query(models.Product)

        if search:
            query = query.filter(
                or_(
                    models.Product.nom.ilike(f"%{search}%"),
                    models.Product.code.ilike(f"%{search}%"),
                )
            )

        if category_id is not None:
            query = query.filter(models.Product.categorie_id == category_id)

        if actif is not None:
            query = query.filter(models.Product.actif == actif)

        total = query.count()
        products = query.offset(skip).limit(limit).all()

        return products, total

    def get_product(self, product_id: int) -> Optional[models.Product]:
        """Récupérer un produit par son ID"""
        return (
            self.db.query(models.Product)
            .filter(models.Product.id == product_id)
            .first()
        )

    def create_product(self, product: schemas.ProductCreate) -> models.Product:
        """Créer un nouveau produit"""
        db_product = models.Product(**product.dict())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def update_product(
        self, product_id: int, product_update: schemas.ProductUpdate
    ) -> Optional[models.Product]:
        """Mettre à jour un produit"""
        db_product = self.get_product(product_id)
        if not db_product:
            return None

        update_data = product_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)

        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def delete_product(self, product_id: int) -> bool:
        """Supprimer un produit (désactivation logique)"""
        db_product = self.get_product(product_id)
        if not db_product:
            return False

        db_product.actif = False
        self.db.commit()
        return True


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_categories(self) -> List[models.Category]:
        """Récupérer toutes les catégories"""
        return self.db.query(models.Category).all()

    def get_category(self, category_id: int) -> Optional[models.Category]:
        """Récupérer une catégorie par son ID"""
        return (
            self.db.query(models.Category)
            .filter(models.Category.id == category_id)
            .first()
        )

    def create_category(self, category: schemas.CategoryCreate) -> models.Category:
        """Créer une nouvelle catégorie"""
        db_category = models.Category(**category.dict())
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def update_category(
        self, category_id: int, category_update: schemas.CategoryUpdate
    ) -> Optional[models.Category]:
        """Mettre à jour une catégorie"""
        db_category = self.get_category(category_id)
        if not db_category:
            return None

        update_data = category_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)

        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def delete_category(self, category_id: int) -> bool:
        """Supprimer une catégorie"""
        db_category = self.get_category(category_id)
        if not db_category:
            return False

        self.db.delete(db_category)
        self.db.commit()
        return True


class StockService:
    def __init__(self, db: Session):
        self.db = db

    def get_stock_info(self, product_id: int) -> Optional[schemas.StockInfo]:
        """Obtenir les informations de stock d'un produit"""
        product = (
            self.db.query(models.Product)
            .filter(models.Product.id == product_id)
            .first()
        )
        if not product:
            return None

        # Déterminer le statut du stock
        if product.quantite_stock == 0:
            status = "rupture"
        elif product.quantite_stock <= product.seuil_alerte:
            status = "faible"
        elif product.quantite_stock > product.seuil_alerte * 3:
            status = "surstock"
        else:
            status = "normal"

        # Obtenir le dernier mouvement
        dernier_mouvement = (
            self.db.query(models.StockMovement)
            .filter(models.StockMovement.product_id == product_id)
            .order_by(models.StockMovement.date_mouvement.desc())
            .first()
        )

        return schemas.StockInfo(
            product_id=product_id,
            quantite_stock=product.quantite_stock,
            seuil_alerte=product.seuil_alerte,
            status=status,
            dernier_mouvement=(
                dernier_mouvement.date_mouvement if dernier_mouvement else None
            ),
        )

    def adjust_stock(
        self, product_id: int, adjustment: schemas.StockAdjustment
    ) -> Optional[models.Product]:
        """Ajuster le stock d'un produit"""
        product = (
            self.db.query(models.Product)
            .filter(models.Product.id == product_id)
            .first()
        )
        if not product:
            return None

        # Créer le mouvement de stock
        movement = models.StockMovement(
            product_id=product_id,
            type_mouvement="ajustement",
            quantite=adjustment.quantite,
            raison=adjustment.raison,
            reference=adjustment.reference,
            utilisateur=adjustment.utilisateur,
        )

        # Mettre à jour le stock
        product.quantite_stock += adjustment.quantite
        if product.quantite_stock < 0:
            product.quantite_stock = 0

        self.db.add(movement)
        self.db.commit()
        self.db.refresh(product)

        # Vérifier et créer des alertes si nécessaire
        self._check_stock_alerts(product)

        return product

    def reduce_stock(
        self,
        product_id: int,
        quantity: int,
        raison: str,
        reference: Optional[str] = None,
    ) -> Optional[dict]:
        """Réduire le stock d'un produit"""
        product = (
            self.db.query(models.Product)
            .filter(models.Product.id == product_id)
            .first()
        )
        if not product:
            return None

        if product.quantite_stock < quantity:
            return None  # Stock insuffisant

        # Créer le mouvement de stock
        movement = models.StockMovement(
            product_id=product_id,
            type_mouvement="sortie",
            quantite=quantity,
            raison=raison,
            reference=reference,
            utilisateur="system",
        )

        # Mettre à jour le stock
        product.quantite_stock -= quantity

        self.db.add(movement)
        self.db.commit()
        self.db.refresh(product)

        # Vérifier et créer des alertes si nécessaire
        self._check_stock_alerts(product)

        return {
            "product_id": product_id,
            "new_stock": product.quantite_stock,
            "movement_id": movement.id,
        }

    def increase_stock(
        self,
        product_id: int,
        quantity: int,
        raison: str,
        reference: Optional[str] = None,
    ) -> Optional[dict]:
        """Augmenter le stock d'un produit"""
        product = (
            self.db.query(models.Product)
            .filter(models.Product.id == product_id)
            .first()
        )
        if not product:
            return None

        # Créer le mouvement de stock
        movement = models.StockMovement(
            product_id=product_id,
            type_mouvement="entree",
            quantite=quantity,
            raison=raison,
            reference=reference,
            utilisateur="system",
        )

        # Mettre à jour le stock
        product.quantite_stock += quantity

        self.db.add(movement)
        self.db.commit()
        self.db.refresh(product)

        # Vérifier et créer des alertes si nécessaire
        self._check_stock_alerts(product)

        return {
            "product_id": product_id,
            "new_stock": product.quantite_stock,
            "movement_id": movement.id,
        }

    def get_stock_movements(
        self,
        product_id: Optional[int] = None,
        type_mouvement: Optional[str] = None,
        limit: int = 50,
    ) -> List[models.StockMovement]:
        """Récupérer les mouvements de stock"""
        query = self.db.query(models.StockMovement)

        if product_id:
            query = query.filter(models.StockMovement.product_id == product_id)

        if type_mouvement:
            query = query.filter(models.StockMovement.type_mouvement == type_mouvement)

        return (
            query.order_by(models.StockMovement.date_mouvement.desc())
            .limit(limit)
            .all()
        )

    def create_stock_movement(
        self, movement: schemas.StockMovementCreate
    ) -> models.StockMovement:
        """Créer un nouveau mouvement de stock"""
        db_movement = models.StockMovement(**movement.dict())
        self.db.add(db_movement)
        self.db.commit()
        self.db.refresh(db_movement)
        return db_movement

    def get_stock_alerts(
        self, resolu: Optional[bool] = None, type_alerte: Optional[str] = None
    ) -> List[models.StockAlert]:
        """Récupérer les alertes de stock"""
        query = self.db.query(models.StockAlert)

        if resolu is not None:
            query = query.filter(models.StockAlert.resolu == resolu)

        if type_alerte:
            query = query.filter(models.StockAlert.type_alerte == type_alerte)

        return query.order_by(models.StockAlert.date_creation.desc()).all()

    def update_stock_alert(
        self, alert_id: int, alert_update: schemas.StockAlertUpdate
    ) -> Optional[models.StockAlert]:
        """Mettre à jour une alerte de stock"""
        alert = (
            self.db.query(models.StockAlert)
            .filter(models.StockAlert.id == alert_id)
            .first()
        )
        if not alert:
            return None

        update_data = alert_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(alert, field, value)

        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_inventory_summary(self) -> schemas.InventorySummary:
        """Obtenir un résumé de l'inventaire"""
        total_products = self.db.query(models.Product).count()
        active_products = (
            self.db.query(models.Product).filter(models.Product.actif == True).count()
        )

        # Produits en rupture
        out_of_stock = (
            self.db.query(models.Product)
            .filter(models.Product.quantite_stock == 0)
            .count()
        )

        # Produits avec stock faible
        low_stock = (
            self.db.query(models.Product)
            .filter(
                and_(
                    models.Product.quantite_stock > 0,
                    models.Product.quantite_stock <= models.Product.seuil_alerte,
                )
            )
            .count()
        )

        # Valeur totale du stock
        total_value = (
            self.db.query(
                func.sum(models.Product.quantite_stock * models.Product.prix_unitaire)
            ).scalar()
            or 0
        )

        return schemas.InventorySummary(
            total_products=total_products,
            active_products=active_products,
            out_of_stock=out_of_stock,
            low_stock=low_stock,
            total_value=float(total_value),
        )

    def get_stock_status(self, product_id: int) -> Optional[schemas.ProductStockStatus]:
        """Obtenir le statut complet du stock d'un produit"""
        product = (
            self.db.query(models.Product)
            .filter(models.Product.id == product_id)
            .first()
        )
        if not product:
            return None

        # Récupérer les derniers mouvements
        recent_movements = (
            self.db.query(models.StockMovement)
            .filter(models.StockMovement.product_id == product_id)
            .order_by(models.StockMovement.date_mouvement.desc())
            .limit(10)
            .all()
        )

        # Récupérer les alertes actives
        active_alerts = (
            self.db.query(models.StockAlert)
            .filter(
                and_(
                    models.StockAlert.product_id == product_id,
                    models.StockAlert.resolu == False,
                )
            )
            .all()
        )

        return schemas.ProductStockStatus(
            product_id=product_id,
            current_stock=product.quantite_stock,
            alert_threshold=product.seuil_alerte,
            recent_movements=recent_movements,
            active_alerts=active_alerts,
        )

    def _check_stock_alerts(self, product: models.Product):
        """Vérifier et créer des alertes de stock si nécessaire"""
        # Alerte de rupture de stock
        if product.quantite_stock == 0:
            self._create_alert(
                product.id, "rupture", f"Produit {product.nom} en rupture de stock"
            )

        # Alerte de stock faible
        elif product.quantite_stock <= product.seuil_alerte:
            self._create_alert(
                product.id,
                "faible",
                f"Stock faible pour {product.nom} ({product.quantite_stock} restants)",
            )

        # Alerte de surstock
        elif product.quantite_stock > product.seuil_alerte * 3:
            self._create_alert(
                product.id,
                "surstock",
                f"Surstock détecté pour {product.nom} ({product.quantite_stock} en stock)",
            )

    def _create_alert(self, product_id: int, type_alerte: str, message: str):
        """Créer une alerte de stock"""
        # Vérifier si une alerte similaire existe déjà
        existing_alert = (
            self.db.query(models.StockAlert)
            .filter(
                and_(
                    models.StockAlert.product_id == product_id,
                    models.StockAlert.type_alerte == type_alerte,
                    models.StockAlert.resolu == False,
                )
            )
            .first()
        )

        if not existing_alert:
            alert = models.StockAlert(
                product_id=product_id,
                type_alerte=type_alerte,
                message=message,
                resolu=False,
            )
            self.db.add(alert)
            self.db.commit()
