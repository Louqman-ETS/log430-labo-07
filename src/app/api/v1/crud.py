from sqlalchemy.orm import Session
from typing import Any, Dict, Optional, List
from sqlalchemy import asc, desc, func

from src.app.models.models import Produit, Categorie, Magasin, Vente, Caisse, LigneVente
from src.app.api.v1.models import (
    ProductCreate,
    ProductUpdate,
    StoreCreate,
    StoreUpdate,
    GlobalSummary,
    StorePerformance,
    TopProduct,
)


def get_product(db: Session, product_id: int) -> Optional[Produit]:
    return db.query(Produit).filter(Produit.id == product_id).first()


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    sort: str = "id",
    order: str = "asc",
    category: Optional[str] = None,
) -> List[Produit]:
    query = db.query(Produit)

    if category:
        query = query.join(Categorie).filter(Categorie.nom == category)

    order_by = None
    if hasattr(Produit, sort):
        if order == "asc":
            order_by = asc(getattr(Produit, sort))
        else:
            order_by = desc(getattr(Produit, sort))

    if order_by is not None:
        query = query.order_by(order_by)

    return query.offset(skip).limit(limit).all()


def get_products_count(db: Session, category: Optional[str] = None) -> int:
    query = db.query(Produit)
    if category:
        query = query.join(Categorie).filter(Categorie.nom == category)
    return query.count()


def create_product(db: Session, *, obj_in: ProductCreate) -> Produit:
    db_obj = Produit(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_product(db: Session, *, db_obj: Produit, obj_in: ProductUpdate) -> Produit:
    update_data = obj_in.dict(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_product(db: Session, *, db_obj: Produit) -> Produit:
    db.delete(db_obj)
    db.commit()
    return db_obj


# Store CRUD
def get_store(db: Session, store_id: int) -> Optional[Magasin]:
    return db.query(Magasin).filter(Magasin.id == store_id).first()


def get_stores(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> List[Magasin]:
    return db.query(Magasin).offset(skip).limit(limit).all()


def get_stores_count(db: Session) -> int:
    return db.query(Magasin).count()


def create_store(db: Session, *, obj_in: StoreCreate) -> Magasin:
    db_obj = Magasin(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_store(db: Session, *, db_obj: Magasin, obj_in: StoreUpdate) -> Magasin:
    update_data = obj_in.dict(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_store(db: Session, *, db_obj: Magasin) -> Magasin:
    db.delete(db_obj)
    db.commit()
    return db_obj


# Reporting CRUDs
def get_global_summary(db: Session) -> GlobalSummary:
    total_revenue = db.query(func.sum(Vente.montant_total)).scalar() or 0
    total_sales_count = db.query(Vente).count()
    average_ticket = total_revenue / total_sales_count if total_sales_count > 0 else 0

    return GlobalSummary(
        total_revenue=total_revenue,
        total_sales_count=total_sales_count,
        average_ticket=average_ticket,
    )


def get_performance_by_store(db: Session) -> List[StorePerformance]:
    results = (
        db.query(
            Magasin.id.label("store_id"),
            Magasin.nom.label("store_name"),
            func.count(Vente.id).label("sales_count"),
            func.sum(Vente.montant_total).label("revenue"),
            func.avg(Vente.montant_total).label("average_ticket"),
        )
        .select_from(Magasin)
        .outerjoin(Caisse, Magasin.id == Caisse.magasin_id)
        .outerjoin(Vente, Caisse.id == Vente.caisse_id)
        .group_by(Magasin.id, Magasin.nom)
        .order_by(desc("revenue"))
        .all()
    )

    # Coalesce None values to 0
    return [
        StorePerformance(
            store_id=r.store_id,
            store_name=r.store_name,
            sales_count=r.sales_count or 0,
            revenue=r.revenue or 0,
            average_ticket=r.average_ticket or 0,
        )
        for r in results
    ]


def get_top_selling_products(
    db: Session, *, limit: int = 15, store_id: Optional[int] = None
) -> List[TopProduct]:
    query = (
        db.query(
            Produit.code.label("product_code"),
            Produit.nom.label("product_name"),
            func.sum(LigneVente.quantite).label("total_quantity_sold"),
            func.sum(LigneVente.quantite * LigneVente.prix_unitaire).label(
                "total_revenue"
            ),
            func.count(func.distinct(Vente.id)).label("total_orders"),
        )
        .select_from(Produit)
        .join(LigneVente, Produit.id == LigneVente.produit_id)
        .join(Vente, LigneVente.vente_id == Vente.id)
    )

    if store_id:
        query = query.join(Caisse, Vente.caisse_id == Caisse.id).filter(
            Caisse.magasin_id == store_id
        )

    results = (
        query.group_by(Produit.id, Produit.code, Produit.nom)
        .order_by(desc("total_quantity_sold"))
        .limit(limit)
        .all()
    )

    return [TopProduct(**r._asdict()) for r in results]
