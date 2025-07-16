import uuid
import time
import logging
import httpx
import requests
import os
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from src.models import (
    Saga, SagaStepExecution, SagaEvent,
    SagaState, SagaStep, SagaStepStatus
)
from src.schemas import (
    OrderProcessingSagaRequest, StockCheckResponse, 
    StockReservationResponse, OrderCreationResponse, PaymentProcessingResponse
)
from src.metrics_service import metrics_service

logger = logging.getLogger(__name__)


class SagaOrchestrator:
    """Orchestrateur principal des sagas"""

    def __init__(self, db: Session):
        self.db = db
        
        # Configuration des services externes via variables d'environnement
        self.inventory_api_url = os.getenv("INVENTORY_API_URL", "http://inventory-api-1:8001")
        self.ecommerce_api_url = os.getenv("ECOMMERCE_API_URL", "http://ecommerce-api:8000")
        self.retail_api_url = os.getenv("RETAIL_API_URL", "http://retail-api:8002")
        self.reporting_api_url = os.getenv("REPORTING_API_URL", "http://reporting-api:8005")
        
        # Clé API pour Kong
        self.kong_api_key = os.getenv("KONG_API_KEY", "admin-api-key-12345")
        
        # Configuration HTTP client avec headers d'authentification
        self.http_timeout = 30.0
        self.http_headers = {
            "apikey": self.kong_api_key,
            "Content-Type": "application/json"
        }
        
        logger.info(f"🔧 Saga Orchestrator configured with:")
        logger.info(f"  - Inventory API: {self.inventory_api_url}")
        logger.info(f"  - Ecommerce API: {self.ecommerce_api_url}")
        logger.info(f"  - API Key: {self.kong_api_key[:10]}...")
        
        # Définition des étapes de la saga et leurs compensations
        self.saga_steps = [
            (SagaStep.CHECK_STOCK, None),
            (SagaStep.RESERVE_STOCK, SagaStep.RELEASE_STOCK),
            (SagaStep.CREATE_ORDER, SagaStep.CANCEL_ORDER),
            (SagaStep.PROCESS_PAYMENT, SagaStep.REFUND_PAYMENT),
            (SagaStep.CONFIRM_ORDER, None),
        ]

    async def _make_http_request(self, method: str, url: str, **kwargs):
        """Fait une requête HTTP isolée et robuste en utilisant requests synchrone"""
        logger.info(f"🌐 Making {method} request to {url} (using requests)")
        
        # Utiliser requests synchrone dans un thread pool pour éviter les conflits async
        import asyncio
        import functools
        
        def sync_request():
            session = requests.Session()
            session.headers.update(self.http_headers)
            
            try:
                response = session.request(
                    method=method,
                    url=url,
                    timeout=self.http_timeout,
                    **kwargs
                )
                logger.info(f"✅ {method} {url} -> {response.status_code} (requests)")
                return response
            finally:
                session.close()
        
        # Exécuter dans un thread pool pour ne pas bloquer l'event loop
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, sync_request)
        return response

    async def start_order_processing_saga(self, request: OrderProcessingSagaRequest) -> str:
        """Démarre une saga de traitement de commande"""
        saga_id = str(uuid.uuid4())
        
        logger.info(f"🚀 Starting order processing saga {saga_id}")
        
        # Créer la saga en base
        saga = Saga(
            saga_id=saga_id,
            saga_type="order_processing",
            state=SagaState.PENDING,
            payload=request.dict(),
            started_at=datetime.utcnow()
        )
        
        self.db.add(saga)
        self.db.commit()
        
        # Enregistrer l'événement de début
        await self._record_event(saga_id, "saga_started", {"request": request.dict()})
        
        # Enregistrer le début dans les métriques
        metrics_service.record_saga_started("order_processing")
        
        # Démarrer l'exécution asynchrone
        try:
            await self._execute_saga(saga_id)
        except Exception as e:
            logger.error(f"❌ Error executing saga {saga_id}: {e}")
            await self._handle_saga_failure(saga_id, str(e))
        
        return saga_id

    async def _execute_saga(self, saga_id: str):
        """Exécute une saga étape par étape"""
        saga = self._get_saga(saga_id)
        if not saga:
            raise ValueError(f"Saga {saga_id} not found")
        
        logger.info(f"⚙️ Executing saga {saga_id}")
        
        # Mettre à jour l'état
        await self._update_saga_state(saga_id, SagaState.STOCK_CHECKING)
        
        executed_steps = []
        
        try:
            # Exécuter chaque étape séquentiellement
            for step_order, (step, compensation_step) in enumerate(self.saga_steps):
                logger.info(f"🔄 About to execute step {step.value} (order {step_order})")
                step_result = await self._execute_step(saga_id, step, step_order, compensation_step)
                logger.info(f"🔄 Completed step {step.value}, result success: {step_result.get('success', False)}")
                executed_steps.append((step, step_result))
                
                # Vérifier si l'étape a échoué
                if not step_result.get("success", False):
                    raise Exception(f"Step {step.value} failed: {step_result.get('error', 'Unknown error')}")
            
            # Toutes les étapes ont réussi
            await self._complete_saga(saga_id, {"order_id": executed_steps[-1][1].get("order_id")})
            
        except Exception as e:
            logger.error(f"❌ Saga {saga_id} failed at step execution: {e}")
            
            # Déclencher la compensation
            await self._compensate_saga(saga_id, executed_steps)

    async def _execute_step(self, saga_id: str, step: SagaStep, step_order: int, compensation_step: Optional[SagaStep]) -> Dict[str, Any]:
        """Exécute une étape spécifique de la saga"""
        start_time = time.time()
        
        logger.info(f"🔧 Executing step {step.value} for saga {saga_id}")
        
        # Créer l'enregistrement d'exécution de l'étape
        step_execution = SagaStepExecution(
            saga_id=saga_id,
            step=step,
            step_order=step_order,
            status=SagaStepStatus.RUNNING,
            compensation_step=compensation_step,
            started_at=datetime.utcnow()
        )
        
        self.db.add(step_execution)
        self.db.commit()
        
        try:
            # Récupérer les données de la saga
            saga = self._get_saga(saga_id)
            request_data = saga.payload
            
            # Exécuter l'étape selon son type
            if step == SagaStep.CHECK_STOCK:
                result = await self._check_stock(request_data)
                await self._update_saga_state(saga_id, SagaState.STOCK_CHECKING)
                
            elif step == SagaStep.RESERVE_STOCK:
                result = await self._reserve_stock(request_data)
                await self._update_saga_state(saga_id, SagaState.STOCK_RESERVED)
                
            elif step == SagaStep.CREATE_ORDER:
                result = await self._create_order(request_data)
                await self._update_saga_state(saga_id, SagaState.ORDER_CREATED)
                
            elif step == SagaStep.PROCESS_PAYMENT:
                result = await self._process_payment(request_data)
                await self._update_saga_state(saga_id, SagaState.PAYMENT_COMPLETED)
                
            elif step == SagaStep.CONFIRM_ORDER:
                result = await self._confirm_order(request_data)
                
            else:
                raise ValueError(f"Unknown step: {step.value}")
            
            # Calculer la durée
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Mettre à jour l'exécution de l'étape
            step_execution.status = SagaStepStatus.COMPLETED
            step_execution.output_data = result
            step_execution.completed_at = datetime.utcnow()
            step_execution.duration_ms = duration_ms
            
            self.db.commit()
            
            # Enregistrer l'événement
            await self._record_event(saga_id, "step_completed", {
                "step": step.value,
                "duration_ms": duration_ms,
                "result": result
            })
            
            # Enregistrer les métriques d'étape
            metrics_service.record_saga_step("order_processing", step.value, "success", duration_ms / 1000.0)
            
            logger.info(f"✅ Step {step.value} completed for saga {saga_id} in {duration_ms}ms")
            
            return {"success": True, **result}
            
        except Exception as e:
            # Calculer la durée même en cas d'erreur
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Mettre à jour l'exécution de l'étape avec l'erreur
            step_execution.status = SagaStepStatus.FAILED
            step_execution.error_message = str(e)
            step_execution.completed_at = datetime.utcnow()
            step_execution.duration_ms = duration_ms
            
            self.db.commit()
            
            # Enregistrer l'événement d'erreur
            await self._record_event(saga_id, "step_failed", {
                "step": step.value,
                "error": str(e),
                "duration_ms": duration_ms
            })
            
            # Enregistrer les métriques d'échec d'étape
            metrics_service.record_saga_step("order_processing", step.value, "failed", duration_ms / 1000.0)
            
            logger.error(f"❌ Step {step.value} failed for saga {saga_id}: {e}")
            
            return {"success": False, "error": str(e)}

    async def _check_stock(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Vérifie la disponibilité du stock pour tous les produits"""
        products = request_data["products"]
        stock_check_results = []
        
        # Vérifier si on doit simuler un échec
        if request_data.get("simulate_failure") == "stock":
            raise Exception("Simulated stock check failure")
        
        for product in products:
            product_id = product["product_id"]
            requested_quantity = product["quantity"]
            
            response = await self._make_http_request(
                "GET",
                f"{self.inventory_api_url}/api/v1/products/{product_id}/stock"
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to check stock for product {product_id}")
                
            stock_data = response.json()
            available_quantity = stock_data["quantite_stock"]
            
            sufficient = available_quantity >= requested_quantity
            
            stock_check_results.append({
                "product_id": product_id,
                "requested_quantity": requested_quantity,
                "available_quantity": available_quantity,
                "sufficient": sufficient
            })
            
            if not sufficient:
                raise Exception(f"Insufficient stock for product {product_id}: requested {requested_quantity}, available {available_quantity}")
        
        return {"stock_checks": stock_check_results, "all_sufficient": True}

    async def _reserve_stock(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Réserve le stock pour tous les produits"""
        logger.info("🔒 Starting stock reservation...")
        products = request_data["products"]
        reservations = []
        
        for product in products:
            product_id = product["product_id"]
            quantity = product["quantity"]
            
            logger.info(f"📦 Reserving {quantity} units of product {product_id}")
            response = await self._make_http_request(
                "PUT",
                f"{self.inventory_api_url}/api/v1/stock/products/{product_id}/stock/reduce",
                params={
                    "quantity": quantity,
                    "raison": f"Réservation saga {request_data.get('saga_id', 'unknown')}",
                    "reference": f"saga_{request_data.get('saga_id', 'unknown')}"
                }
            )
                
            if response.status_code != 200:
                raise Exception(f"Failed to reserve stock for product {product_id}")
                
            reservation_data = response.json()
            reservations.append({
                "product_id": product_id,
                "reserved_quantity": quantity,
                "new_stock_level": reservation_data["new_stock"]
            })
        
        return {"reservations": reservations}

    async def _create_order(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée la commande dans le service ecommerce"""
        
        # Étape 1: Vérifier que le customer_id fourni existe
        requested_customer_id = request_data["customer_id"]
        
        # Vérifier si le customer existe
        customer_response = await self._make_http_request(
            "GET",
            f"{self.ecommerce_api_url}/api/v1/customers/{requested_customer_id}"
        )
        
        if customer_response.status_code != 200:
            raise Exception(f"Customer {requested_customer_id} not found. Customer must exist before creating order.")
        
        logger.info(f"✅ Customer {requested_customer_id} found, proceeding with order")
        actual_customer_id = requested_customer_id
        
        # Étape 2: Créer un cart avec l'ID du customer réellement créé
        cart_data = {
            "customer_id": actual_customer_id
        }
        
        cart_response = await self._make_http_request(
            "POST",
            f"{self.ecommerce_api_url}/api/v1/carts",
            json=cart_data
        )
        
        if cart_response.status_code != 201:
            raise Exception(f"Failed to create cart: {cart_response.text}")
        
        cart = cart_response.json()
        cart_id = cart["id"]
        
        # Étape 3: Ajouter les produits au cart
        for product in request_data["products"]:
            item_data = {
                "product_id": product["product_id"],
                "quantity": product["quantity"]
            }
            
            item_response = await self._make_http_request(
                "POST",
                f"{self.ecommerce_api_url}/api/v1/carts/{cart_id}/items",
                json=item_data
            )
            
            if item_response.status_code != 201:
                raise Exception(f"Failed to add item to cart: {item_response.text}")
        
        # Étape 4: Checkout du cart
        checkout_data = {
            "cart_id": cart_id,
            "customer_id": actual_customer_id,
            "shipping_address": request_data["shipping_address"],
            "billing_address": request_data["billing_address"],
            "payment_method": request_data.get("payment_method", "credit_card")
        }
        
        response = await self._make_http_request(
            "POST",
            f"{self.ecommerce_api_url}/api/v1/orders/checkout",
            json=checkout_data
        )
            
        if response.status_code != 201:
            raise Exception(f"Failed to create order: {response.text}")
            
        order_data = response.json()
            
        return {
            "customer_id": actual_customer_id,
            "cart_id": cart_id,
            "order_id": order_data["id"],
            "order_number": order_data["order_number"],
            "total_amount": float(order_data["total_amount"]),
            "status": order_data["status"]
        }

    async def _process_payment(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Traite le paiement (simulé)"""
        # Vérifier si on doit simuler un échec de paiement
        if request_data.get("simulate_failure") == "payment":
            raise Exception("Simulated payment processing failure")
        
        # Calculer le montant total
        total_amount = sum(product["quantity"] * product["price"] for product in request_data["products"])
        
        # Simuler le traitement du paiement
        payment_id = str(uuid.uuid4())
        transaction_id = f"txn_{int(time.time())}"
        
        # Simuler un délai de traitement
        await asyncio.sleep(0.1)
        
        return {
            "payment_id": payment_id,
            "amount": total_amount,
            "status": "completed",
            "transaction_id": transaction_id
        }

    async def _confirm_order(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Confirme la commande"""
        # Cette étape finalise la commande et peut inclure des notifications
        return {"confirmed": True, "confirmation_time": datetime.utcnow().isoformat()}

    async def _compensate_saga(self, saga_id: str, executed_steps: List[tuple]):
        """Exécute les actions de compensation pour les étapes réussies"""
        logger.info(f"🔄 Starting compensation for saga {saga_id}")
        
        await self._update_saga_state(saga_id, SagaState.COMPENSATING)
        
        # Exécuter les compensations dans l'ordre inverse
        for step, step_result in reversed(executed_steps):
            if step_result.get("success"):
                compensation_step = self._get_compensation_step(step)
                if compensation_step:
                    try:
                        await self._execute_compensation(saga_id, compensation_step, step_result)
                    except Exception as e:
                        logger.error(f"❌ Compensation failed for step {step.value}: {e}")
        
        await self._update_saga_state(saga_id, SagaState.COMPENSATED)
        logger.info(f"✅ Compensation completed for saga {saga_id}")

    def _get_compensation_step(self, step: SagaStep) -> Optional[SagaStep]:
        """Retourne l'étape de compensation pour une étape donnée"""
        for saga_step, compensation_step in self.saga_steps:
            if saga_step == step:
                return compensation_step
        return None

    async def _execute_compensation(self, saga_id: str, compensation_step: SagaStep, original_step_result: Dict[str, Any]):
        """Exécute une action de compensation"""
        logger.info(f"🔄 Executing compensation {compensation_step.value} for saga {saga_id}")
        
        # Enregistrer la compensation dans les métriques
        metrics_service.record_compensation("order_processing", compensation_step.value)
        
        saga = self._get_saga(saga_id)
        request_data = saga.payload
        
        if compensation_step == SagaStep.RELEASE_STOCK:
            await self._release_stock(request_data, original_step_result)
        elif compensation_step == SagaStep.CANCEL_ORDER:
            await self._cancel_order(original_step_result)
        elif compensation_step == SagaStep.REFUND_PAYMENT:
            await self._refund_payment(original_step_result)

    async def _release_stock(self, request_data: Dict[str, Any], reservation_result: Dict[str, Any]):
        """Libère le stock réservé"""
        products = request_data["products"]
        
        for product in products:
            product_id = product["product_id"]
            quantity = product["quantity"]
            
            await self._make_http_request(
                "PUT",
                f"{self.inventory_api_url}/api/v1/stock/products/{product_id}/stock/increase",
                params={
                    "quantity": quantity,
                    "raison": f"Compensation saga {request_data.get('saga_id', 'unknown')}",
                    "reference": f"compensation_saga_{request_data.get('saga_id', 'unknown')}"
                }
            )

    async def _cancel_order(self, order_result: Dict[str, Any]):
        """Annule la commande créée"""
        order_id = order_result.get("order_id")
        if order_id:
            await self._make_http_request(
                "POST", 
                f"{self.ecommerce_api_url}/api/v1/orders/{order_id}/cancel"
            )

    async def _refund_payment(self, payment_result: Dict[str, Any]):
        """Effectue le remboursement (simulé)"""
        payment_id = payment_result.get("payment_id")
        amount = payment_result.get("amount")
        logger.info(f"💰 Simulated refund of {amount} for payment {payment_id}")

    async def _complete_saga(self, saga_id: str, result: Dict[str, Any]):
        """Marque la saga comme terminée avec succès"""
        saga = self._get_saga(saga_id)
        saga.state = SagaState.COMPLETED
        saga.result = result
        saga.completed_at = datetime.utcnow()
        
        # Calculer la durée totale
        if saga.started_at:
            duration = (saga.completed_at - saga.started_at).total_seconds()
            metrics_service.record_saga_completed("order_processing", duration)
        
        self.db.commit()
        
        await self._record_event(saga_id, "saga_completed", result)
        logger.info(f"✅ Saga {saga_id} completed successfully")

    async def _handle_saga_failure(self, saga_id: str, error_message: str):
        """Gère l'échec d'une saga"""
        saga = self._get_saga(saga_id)
        saga.state = SagaState.FAILED
        saga.error_message = error_message
        saga.failed_at = datetime.utcnow()
        
        # Calculer la durée totale même en cas d'échec
        if saga.started_at:
            duration = (saga.failed_at - saga.started_at).total_seconds()
            metrics_service.record_saga_failed("order_processing", duration)
        
        self.db.commit()
        
        await self._record_event(saga_id, "saga_failed", {"error": error_message})
        logger.error(f"❌ Saga {saga_id} failed: {error_message}")

    async def _update_saga_state(self, saga_id: str, new_state: SagaState):
        """Met à jour l'état d'une saga"""
        saga = self._get_saga(saga_id)
        old_state = saga.state
        saga.state = new_state
        saga.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        await self._record_event(saga_id, "state_changed", {
            "old_state": old_state.value,
            "new_state": new_state.value
        })

    async def _record_event(self, saga_id: str, event_type: str, event_data: Dict[str, Any]):
        """Enregistre un événement de saga"""
        event = SagaEvent(
            saga_id=saga_id,
            event_type=event_type,
            event_data=event_data
        )
        
        self.db.add(event)
        self.db.commit()

    def _get_saga(self, saga_id: str) -> Optional[Saga]:
        """Récupère une saga par son ID"""
        return self.db.query(Saga).filter(Saga.saga_id == saga_id).first()

    def get_saga_status(self, saga_id: str) -> Optional[Saga]:
        """Récupère le statut complet d'une saga"""
        return self.db.query(Saga).filter(Saga.saga_id == saga_id).first()

    def get_sagas(self, skip: int = 0, limit: int = 100) -> List[Saga]:
        """Récupère la liste des sagas"""
        return self.db.query(Saga).offset(skip).limit(limit).all()

    async def cleanup(self):
        """Nettoie les ressources"""
        pass  # Plus besoin de nettoyer le client HTTP puisqu'on utilise des clients temporaires


# Import asyncio après la définition de la classe pour éviter les problèmes d'import circulaire
import asyncio 