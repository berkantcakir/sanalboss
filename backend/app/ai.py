from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class PlanStep:
    title: str
    detail: str


@dataclass
class AIPlanResponse:
    plan_steps: List[PlanStep]
    motivation_message: str
    metadata: Dict[str, Any]


class LLMAdapter:
    def __init__(self, model_name: str = "demo-llm") -> None:
        self.model_name = model_name

    def generate_plan(
        self,
        *,
        job_title: str,
        job_description: str,
        feedback: Optional[str] = None,
        failure_reason: Optional[str] = None,
    ) -> AIPlanResponse:
        context = f"İş: {job_title}. {job_description}".strip()
        steps = [
            PlanStep(title="Kapsamı netleştir", detail=f"{context} için hedefleri belirle."),
            PlanStep(title="Adımları sırala", detail="Teslimatları küçük parçalara böl."),
            PlanStep(title="Uygulama", detail="Öncelik sırasına göre adımları uygula."),
            PlanStep(title="Kontrol", detail="Sonuçları gözden geçir ve düzelt."),
        ]
        motivation = "Harika gidiyorsun! Küçük adımlar büyük sonuçlar getirir."
        if feedback:
            steps.insert(
                1,
                PlanStep(
                    title="Geri bildirim analizi",
                    detail=f"Şu geri bildirimi dikkate al: {feedback}",
                ),
            )
            motivation = "Zorluklar normaldir. Geri bildirimini plana dahil ettim!"
        if failure_reason:
            steps.append(
                PlanStep(
                    title="Engelleri kaldır",
                    detail=f"Şu engeli çözmek için alternatif plan üret: {failure_reason}",
                )
            )
            motivation = "Tıkandığın noktalar büyümenin parçası. Yeni bir yol deneyeceğiz!"
        metadata = {
            "model": self.model_name,
            "generated_at": datetime.utcnow().isoformat(),
        }
        return AIPlanResponse(plan_steps=steps, motivation_message=motivation, metadata=metadata)
