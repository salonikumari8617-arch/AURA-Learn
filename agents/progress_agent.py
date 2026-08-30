from dataclasses import dataclass
from typing import Dict,List

from memory.learner_profile import learner_memory


@dataclass
class ProgressAnalysis:
    topic:str
    overall_status:str
    weak_concepts:List[str]
    strong_concepts:List[str]
    trend:str
    reasoning_summary:str


class ProgressAgent:

    def analyze(
        self,
        topic:str,
        concept_performance:Dict[str,float]
    )->ProgressAnalysis:

        profile=learner_memory.get_profile()

        if profile is None:
            raise ValueError("Learner profile not found")

        weak_concepts=[]
        strong_concepts=[]

        values=list(concept_performance.values())

        if not values:
            raise ValueError("Concept performance cannot be empty")

        average=sum(values)/len(values)

        for concept,value in concept_performance.items():

            if value<average:
                weak_concepts.append(concept)

            else:
                strong_concepts.append(concept)


        previous_scores=[
            attempt.score
            for attempt in profile.learning_history
            if attempt.topic==topic
        ]


        current_score=round(average*100,2)

        trend="no_history"

        if previous_scores:

            previous_score=previous_scores[-1]

            if current_score>previous_score:
                trend="improving"

            elif current_score<previous_score:
                trend="declining"

            else:
                trend="stable"


        if len(weak_concepts)==0:
            overall_status="strong"

        elif len(weak_concepts)<len(concept_performance)/2:
            overall_status="developing"

        else:
            overall_status="needs_support"


        reasoning_summary=(
            f"Current concept-level performance produced an "
            f"average score of {current_score}. "
            f"Weak concepts: {weak_concepts}. "
            f"Strong concepts: {strong_concepts}. "
            f"Learning trend: {trend}."
        )


        learner_memory.add_learning_attempt(
            topic=topic,
            score=current_score,
            weak_concepts=weak_concepts,
            strong_concepts=strong_concepts
        )


        return ProgressAnalysis(
            topic=topic,
            overall_status=overall_status,
            weak_concepts=weak_concepts,
            strong_concepts=strong_concepts,
            trend=trend,
            reasoning_summary=reasoning_summary
        )


progress_agent=ProgressAgent()