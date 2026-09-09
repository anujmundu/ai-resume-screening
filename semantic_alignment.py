"""Multi-Dimensional Semantic Alignment Engine for TalentAI.

Evaluates multi-faceted alignment between candidate profiles and Job Descriptions across
Skills, Experience, Education, and Seniority vectors with sublinear TF-IDF embeddings.

100% offline, deterministic, explainable NLP analytics.
"""

from typing import Dict, Any, List, Set, Tuple
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SENIORITY_KEYWORDS = {
    "junior": ["junior", "entry", "associate", "intern", "0-2", "1-2 years"],
    "mid": ["mid", "intermediate", "software engineer", "developer", "2-5", "3-5 years"],
    "senior": ["senior", "lead", "staff", "principal", "architect", "5+", "7+", "10+ years"]
}


def _clean_tokens(items: List[Any]) -> List[str]:
    """Clean and standardize skill strings."""
    result = []
    for item in items:
        if not item:
            continue
        cleaned = str(item).strip().title()
        if len(cleaned) >= 2:
            result.append(cleaned)
    return result


class SemanticAlignmentEngine:
    """Evaluates multi-tier semantic alignment across Skills, Experience, and Education."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")

    def _compute_text_similarity(self, text_a: str, text_b: str) -> float:
        """Compute cosine similarity between two text snippets."""
        if not text_a.strip() or not text_b.strip():
            return 0.0
        try:
            matrix = self.vectorizer.fit_transform([text_a, text_b]).toarray()
            sim = float(cosine_similarity([matrix[0]], [matrix[1]])[0][0])
            return max(0.0, min(1.0, sim))
        except Exception:
            # Fallback to Jaccard set similarity
            tokens_a = set(re.findall(r'\b\w+\b', text_a.lower()))
            tokens_b = set(re.findall(r'\b\w+\b', text_b.lower()))
            if not tokens_a or not tokens_b:
                return 0.0
            return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)

    def evaluate_alignment(self, candidate_doc: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Compute structured multi-dimensional alignment scores."""
        data = candidate_doc.get("data", candidate_doc)
        jd_clean = (job_description or "").strip()

        if not jd_clean:
            return {
                "overall_alignment": float(candidate_doc.get("score", 70)),
                "skills_alignment": 75.0,
                "experience_alignment": 70.0,
                "education_alignment": 75.0,
                "seniority_fit": "Nominal",
                "matched_competencies": data.get("skills", [])[:6],
                "competency_gaps": []
            }

        # 1. Skills Alignment
        candidate_skills = set(_clean_tokens(data.get("skills", [])))
        
        # Extract keywords from JD to compare
        jd_words = set(re.findall(r'\b[A-Za-z0-9\+\#\.-]{2,20}\b', jd_clean.lower()))
        matched_skills = []
        for s in candidate_skills:
            if s.lower() in jd_words:
                matched_skills.append(s)

        # Semantic skill text similarity
        cand_skills_str = " ".join(candidate_skills)
        skills_sim = self._compute_text_similarity(cand_skills_str, jd_clean)
        
        # Blend lexical hit ratio and semantic similarity
        if candidate_skills:
            lexical_ratio = len(matched_skills) / max(1, min(len(candidate_skills), 12))
        else:
            lexical_ratio = 0.0
        
        skills_alignment = round(min(100.0, (lexical_ratio * 55.0 + skills_sim * 45.0 * 100)), 1)
        skills_alignment = max(10.0, skills_alignment)

        # 2. Experience Alignment
        exp_entries = data.get("experience", [])
        exp_texts = []
        for e in exp_entries:
            if isinstance(e, dict):
                exp_texts.append(f"{e.get('role', '')} {e.get('description', '')}")
            else:
                exp_texts.append(str(e))
        exp_composite = " ".join(exp_texts)
        exp_sim = self._compute_text_similarity(exp_composite, jd_clean)
        experience_alignment = round(min(100.0, max(15.0, exp_sim * 100 * 1.35)), 1)

        # 3. Education Alignment
        edu_entries = data.get("education", [])
        edu_texts = []
        has_stem = False
        has_masters_or_phd = False
        for ed in edu_entries:
            ed_str = str(ed).lower()
            edu_texts.append(ed_str)
            if any(term in ed_str for term in ["computer", "engineering", "science", "math", "technology", "mca", "b.tech", "btech"]):
                has_stem = True
            if any(term in ed_str for term in ["master", "m.tech", "mca", "phd", "m.s.", "ms"]):
                has_masters_or_phd = True

        edu_score = 50.0
        if edu_entries:
            edu_score += 20.0
        if has_stem:
            edu_score += 20.0
        if has_masters_or_phd:
            edu_score += 10.0
        education_alignment = round(min(100.0, edu_score), 1)

        # 4. Overall Alignment Composite (45% Skills, 35% Experience, 20% Education)
        overall = round(
            skills_alignment * 0.45 + experience_alignment * 0.35 + education_alignment * 0.20,
            1
        )

        # Seniority Level Classification
        jd_lower = jd_clean.lower()
        if any(w in jd_lower for w in SENIORITY_KEYWORDS["senior"]):
            target_seniority = "Senior / Lead"
        elif any(w in jd_lower for w in SENIORITY_KEYWORDS["junior"]):
            target_seniority = "Junior / Associate"
        else:
            target_seniority = "Mid-Level"

        candidate_text_all = f"{cand_skills_str} {exp_composite}".lower()
        if any(w in candidate_text_all for w in SENIORITY_KEYWORDS["senior"]):
            cand_seniority = "Senior / Lead"
        else:
            cand_seniority = "Mid-Level"

        if target_seniority == cand_seniority:
            seniority_fit = f"High Alignment ({cand_seniority})"
        else:
            seniority_fit = f"Acceptable ({cand_seniority} applying for {target_seniority})"

        # Identify key missing competencies (common tech in JD not found in candidate)
        common_tech_terms = ["Python", "Docker", "Kubernetes", "AWS", "SQL", "React", "Kafka", "Redis", "TypeScript", "CI/CD", "FastAPI"]
        missing_skills = [
            tech for tech in common_tech_terms 
            if tech.lower() in jd_lower and tech not in candidate_skills
        ]

        return {
            "overall_alignment": overall,
            "skills_alignment": skills_alignment,
            "experience_alignment": experience_alignment,
            "education_alignment": education_alignment,
            "seniority_fit": seniority_fit,
            "matched_competencies": matched_skills[:10],
            "competency_gaps": missing_skills[:6]
        }


# Singleton instance
_semantic_aligner = SemanticAlignmentEngine()


def compute_semantic_alignment(candidate_doc: Dict[str, Any], job_description: str) -> Dict[str, Any]:
    """Public helper to evaluate multi-tier semantic alignment."""
    return _semantic_aligner.evaluate_alignment(candidate_doc, job_description)
