"""Candidate Knowledge Graph & Entity Relationships Engine.

Leverages NetworkX to build a heterogeneous graph of:
- Candidate nodes
- Skill nodes (categorized by technical domain)
- Company / Organization nodes
- Role / Title nodes
- Degree / Academic Institution nodes

Graph Analytics:
1. Hub Skill identification via Degree Centrality & Betweenness Centrality.
2. Skill Co-occurrence network & Technical Bridge detection.
3. Candidate Ego-Network extraction for individual profiling & comparative overlap.
4. Adjacent Skill Recommendations via graph neighborhood co-occurrence.
5. Interactive force-directed serialization (nodes, links, clusters) for Web UI.

100% Offline-First, Zero Cloud Spend.
"""

from typing import List, Dict, Any, Optional, Tuple, Set
import re
from collections import Counter
import networkx as nx


# Technical domain vocabulary mapping for skill categorization
SKILL_TAXONOMY = {
    "Backend & Systems": {
        "python", "go", "golang", "c++", "c#", "java", "rust", "django", "fastapi", "flask",
        "spring", "ruby", "rails", "php", "nodejs", "node.js", "graphql", "rest", "grpc",
        "microservices", "multithreading", "asyncio", "celery", "pydantic"
    },
    "Frontend & Web": {
        "react", "react.js", "next.js", "nextjs", "vue", "vue.js", "angular", "svelte",
        "typescript", "javascript", "html", "html5", "css", "css3", "sass", "tailwind",
        "redux", "zustand", "webpack", "vite", "figma"
    },
    "Cloud & DevOps": {
        "docker", "kubernetes", "k8s", "aws", "gcp", "azure", "terraform", "ansible",
        "ci/cd", "github actions", "gitlab", "jenkins", "linux", "helm", "nginx",
        "prometheus", "grafana", "opentelemetry", "cloud"
    },
    "Data & Databases": {
        "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "kafka",
        "rabbitmq", "apache spark", "spark", "snowflake", "bigquery", "airflow",
        "elasticsearch", "cassandra", "sql", "dbt", "databricks"
    },
    "AI, ML & NLP": {
        "machine learning", "deep learning", "nlp", "computer vision", "pytorch",
        "tensorflow", "scikit-learn", "keras", "huggingface", "llm", "llms", "rag",
        "langchain", "transformers", "embeddings", "faiss", "vector search"
    },
    "Security & Compliance": {
        "cybersecurity", "security", "iam", "oauth", "jwt", "penetration testing",
        "soc2", "gdpr", "hipaa", "cryptography", "zero trust", "siem", "firewall"
    }
}


def categorize_skill(skill: str) -> str:
    """Classify a skill into its parent technical domain."""
    skill_clean = skill.strip().lower()
    for domain, domain_skills in SKILL_TAXONOMY.items():
        if skill_clean in domain_skills:
            return domain
        for ds in domain_skills:
            if ds in skill_clean or skill_clean in ds:
                return domain
    return "Core Engineering"


class CandidateKnowledgeGraph:
    """Heterogeneous entity graph tracking Candidates, Skills, Companies, and Roles."""

    def __init__(self, candidates: Optional[List[Dict[str, Any]]] = None):
        self.graph = nx.Graph()
        self.candidates_data: Dict[str, Dict[str, Any]] = {}
        if candidates:
            self.build_graph(candidates)

    def build_graph(self, candidates: List[Dict[str, Any]]):
        """Construct the multi-entity knowledge graph from a list of candidate records.
        Deduplicates applicants by normalized name to ensure all unique uploaded resumes
        are cleanly represented with their complete details and highest evaluation score.
        """
        self.graph.clear()
        self.candidates_data.clear()

        # Deduplicate incoming candidate records by name, keeping highest score / richest data
        deduped = {}
        for cand in candidates:
            cname = (cand.get("candidate_name") or cand.get("data", {}).get("candidate_name") or "").strip()
            cid = str(cand.get("_id") or cand.get("id") or "")
            key = cname.lower() if cname else cid
            if not key:
                continue
            cand_score = int(cand.get("score", 0) or 0)
            if key not in deduped or cand_score > int(deduped[key].get("score", 0) or 0):
                deduped[key] = cand

        candidates_list = list(deduped.values())

        # Co-occurrence tracking across candidate skill pairs
        skill_cooccurrence = Counter()

        for cand in candidates_list:
            cid = str(cand.get("_id") or cand.get("id") or "")
            if not cid:
                continue

            name = cand.get("candidate_name") or cand.get("data", {}).get("candidate_name") or f"Candidate {cid}"
            score = int(cand.get("score", 0) or 0)
            decision = (cand.get("decision") or "review").lower()
            stage = (cand.get("stage") or "screened").lower()
            cdata = cand.get("data") or {}

            # Rich resume metadata
            email = cdata.get("email") or cand.get("email") or ""
            phone = cdata.get("phone") or cand.get("phone") or ""
            title = cdata.get("title") or cand.get("title") or cdata.get("target_role") or cand.get("target_role") or ""
            exp_years = cdata.get("experience_years") or cand.get("experience_years")
            edu_raw = cdata.get("education") or cand.get("education") or ""
            summary = cdata.get("summary") or cand.get("summary") or ""
            memo = cand.get("recruiter_memo") or cdata.get("recruiter_memo") or ""
            integrity = cand.get("integrity_score")
            if integrity is None:
                integrity = cand.get("audit_report", {}).get("integrity_score", 100) if isinstance(cand.get("audit_report"), dict) else 100
            semantic_fit = cand.get("semantic_fit") or 0.0

            # 1. Extract and Link Skills
            cand_skills = cand.get("skills") or cdata.get("skills") or []
            if isinstance(cand_skills, str):
                try:
                    import json
                    cand_skills = json.loads(cand_skills)
                except Exception:
                    cand_skills = [s.strip() for s in cand_skills.split(",") if s.strip()]

            clean_skills = []
            for s in cand_skills:
                s_name = s.strip()
                if not s_name:
                    continue
                clean_skills.append(s_name)
                skill_node_id = f"skill_{s_name.lower()}"
                domain = categorize_skill(s_name)

                if not self.graph.has_node(skill_node_id):
                    self.graph.add_node(
                        skill_node_id,
                        node_type="skill",
                        label=s_name,
                        domain=domain
                    )

                self.graph.add_edge(
                    f"cand_{cid}",
                    skill_node_id,
                    relation="has_skill",
                    weight=1.0
                )

            # Dominant technical domain
            domain_counts = Counter(categorize_skill(s) for s in clean_skills)
            dominant_domain = domain_counts.most_common(1)[0][0] if domain_counts else "Core Engineering"

            self.candidates_data[cid] = {
                "name": name,
                "score": score,
                "decision": decision,
                "stage": stage,
                "domain": dominant_domain,
                "title": title,
                "email": email,
                "phone": phone,
                "experience_years": exp_years,
                "education": edu_raw,
                "summary": summary,
                "recruiter_memo": memo,
                "integrity_score": integrity,
                "semantic_fit": semantic_fit,
                "skills": clean_skills
            }

            cand_node_id = f"cand_{cid}"
            self.graph.add_node(
                cand_node_id,
                node_type="candidate",
                id=cid,
                label=name,
                score=score,
                decision=decision,
                stage=stage,
                domain=dominant_domain,
                title=title,
                email=email,
                phone=phone,
                experience_years=exp_years,
                education=edu_raw,
                summary=summary,
                recruiter_memo=memo,
                integrity_score=integrity,
                semantic_fit=semantic_fit
            )

            # Track pairwise skill co-occurrence
            unique_skills = sorted(list(set(s.lower() for s in clean_skills)))
            for i in range(len(unique_skills)):
                for j in range(i + 1, len(unique_skills)):
                    pair = (unique_skills[i], unique_skills[j])
                    skill_cooccurrence[pair] += 1

            # 2. Extract and Link Companies & Roles from Work Experience
            exp_list = cdata.get("experience") or cand.get("experience") or []
            if isinstance(exp_list, str):
                try:
                    import json
                    exp_list = json.loads(exp_list)
                except Exception:
                    exp_list = []
            elif isinstance(exp_list, dict):
                exp_list = [exp_list]
            elif not isinstance(exp_list, list):
                exp_list = []

            for item in exp_list:
                comp = ""
                role = ""
                if isinstance(item, dict):
                    comp = (item.get("company") or "").strip()
                    role = (item.get("role") or "").strip()
                elif isinstance(item, str):
                    role = item.strip()

                comp = comp.replace('', '').strip()
                role = role.replace('', '').strip()

                if len(comp) > 1 and not comp.isdigit():
                    comp_node_id = f"comp_{comp.lower()}"
                    if not self.graph.has_node(comp_node_id):
                        self.graph.add_node(comp_node_id, node_type="company", label=comp)
                    self.graph.add_edge(cand_node_id, comp_node_id, relation="worked_at", weight=1.0)

                if len(role) > 1 and not role.isdigit():
                    role_node_id = f"role_{role.lower()}"
                    if not self.graph.has_node(role_node_id):
                        self.graph.add_node(role_node_id, node_type="role", label=role)
                    self.graph.add_edge(cand_node_id, role_node_id, relation="held_role", weight=1.0)

            # 3. Extract and Link Education / Degrees
            raw_edu = cdata.get("education") or cand.get("education") or []
            edu_items = []
            if isinstance(raw_edu, str):
                try:
                    import json
                    parsed = json.loads(raw_edu)
                    if isinstance(parsed, list):
                        edu_items = parsed
                    else:
                        edu_items = [raw_edu]
                except Exception:
                    # Clean up bullet points, semicolons, or non-ascii artifacts
                    parts = [p.strip() for p in re.split(r'[;•\ufffd|\n]', raw_edu) if p.strip()]
                    edu_items = parts if parts else [raw_edu.strip()]
            elif isinstance(raw_edu, dict):
                edu_items = [raw_edu]
            elif isinstance(raw_edu, list):
                edu_items = raw_edu

            for item in edu_items:
                degree = ""
                if isinstance(item, dict):
                    degree = (item.get("degree") or item.get("field") or "").strip()
                elif isinstance(item, str):
                    degree = item.strip()

                # Clean up years like (2019) or trailing details
                clean_degree = re.sub(r'\(.*?\)', '', degree).strip()
                clean_degree = clean_degree.replace('', '').strip()
                if len(clean_degree) > 2 and not clean_degree.isdigit():
                    deg_node_id = f"deg_{clean_degree.lower()}"
                    if not self.graph.has_node(deg_node_id):
                        self.graph.add_node(deg_node_id, node_type="degree", label=clean_degree)
                    self.graph.add_edge(cand_node_id, deg_node_id, relation="studied", weight=1.0)

        # 4. Link Skill Co-occurrence Edges (frequency >= 1)
        for (s1, s2), count in skill_cooccurrence.items():
            s1_node = f"skill_{s1}"
            s2_node = f"skill_{s2}"
            if self.graph.has_node(s1_node) and self.graph.has_node(s2_node):
                self.graph.add_edge(s1_node, s2_node, relation="co_occurs", weight=count)

    def get_graph_statistics(self) -> Dict[str, Any]:
        """Compute holistic topological and centrality metrics."""
        total_nodes = self.graph.number_of_nodes()
        total_edges = self.graph.number_of_edges()

        node_types = Counter(data.get("node_type", "unknown") for _, data in self.graph.nodes(data=True))

        # Skill sub-network centrality
        skill_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == "skill"]
        skill_subgraph = self.graph.subgraph(skill_nodes)

        degree_centrality = nx.degree_centrality(self.graph) if total_nodes > 1 else {}
        betweenness_centrality = nx.betweenness_centrality(self.graph) if total_nodes > 1 else {}

        # Top hub skills
        hub_skills = []
        for sn in skill_nodes:
            lbl = self.graph.nodes[sn].get("label", sn)
            domain = self.graph.nodes[sn].get("domain", "Engineering")
            deg = self.graph.degree(sn)
            deg_cent = round(degree_centrality.get(sn, 0.0), 3)
            bet_cent = round(betweenness_centrality.get(sn, 0.0), 3)
            hub_skills.append({
                "skill": lbl,
                "domain": domain,
                "degree": deg,
                "degree_centrality": deg_cent,
                "betweenness_centrality": bet_cent
            })

        hub_skills.sort(key=lambda x: (x["degree"], x["betweenness_centrality"]), reverse=True)

        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "density": round(nx.density(self.graph), 4) if total_nodes > 1 else 0.0,
            "node_breakdown": dict(node_types),
            "top_hub_skills": hub_skills[:12],
            "connected_components": nx.number_connected_components(self.graph) if total_nodes > 0 else 0
        }

    def get_candidate_subgraph(self, candidate_id: str, depth: int = 1) -> Dict[str, Any]:
        """Extract a 1- or 2-hop neighborhood ego-subgraph centered on a specific candidate."""
        cand_node = f"cand_{candidate_id}"
        if not self.graph.has_node(cand_node):
            return {"nodes": [], "links": [], "candidate_id": candidate_id}

        ego_nodes = set([cand_node])
        for _ in range(depth):
            current_layer = list(ego_nodes)
            for n in current_layer:
                ego_nodes.update(self.graph.neighbors(n))

        sub = self.graph.subgraph(ego_nodes)
        return self._serialize_subgraph(sub, focus_id=cand_node)

    def recommend_adjacent_skills(self, candidate_id: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """Recommend complementary skills that co-occur with candidate's existing skills."""
        cand_node = f"cand_{candidate_id}"
        if not self.graph.has_node(cand_node):
            return []

        # Find candidate's current skills
        existing_skills = {
            n for n in self.graph.neighbors(cand_node)
            if self.graph.nodes[n].get("node_type") == "skill"
        }

        candidate_skill_names = {self.graph.nodes[s].get("label", "").lower() for s in existing_skills}

        # Accumulate co-occurrence scores from neighbor skill nodes
        adjacent_scores = Counter()
        for skill_node in existing_skills:
            for neighbor in self.graph.neighbors(skill_node):
                if neighbor.startswith("skill_") and neighbor not in existing_skills:
                    # Weight by edge co-occurrence weight
                    edge_data = self.graph.get_edge_data(skill_node, neighbor) or {}
                    w = edge_data.get("weight", 1.0) if edge_data.get("relation") == "co_occurs" else 1.0
                    adjacent_scores[neighbor] += w

        recommendations = []
        for skill_node, score in adjacent_scores.most_common(top_n):
            s_label = self.graph.nodes[skill_node].get("label", skill_node.replace("skill_", "").title())
            domain = self.graph.nodes[skill_node].get("domain", "Engineering")
            recommendations.append({
                "skill": s_label,
                "domain": domain,
                "affinity_score": round(score, 1),
                "reason": f"Strongly co-occurs in {domain} candidate profiles with your verified skills."
            })

        return recommendations

    def find_skill_bridges(self, top_n: int = 6) -> List[Dict[str, Any]]:
        """Find technical bridge skills that connect multiple disparate domains."""
        skill_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == "skill"]
        if len(skill_nodes) < 3:
            return []

        # Project onto skills-only subgraph
        sub = self.graph.subgraph(skill_nodes)
        if sub.number_of_nodes() < 2:
            return []

        betweenness = nx.betweenness_centrality(sub)
        sorted_skills = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)

        bridges = []
        for s_node, score in sorted_skills[:top_n]:
            lbl = self.graph.nodes[s_node].get("label", s_node)
            domain = self.graph.nodes[s_node].get("domain", "Engineering")
            # Count connected domains
            connected_domains = set()
            for neighbor in self.graph.neighbors(s_node):
                if neighbor.startswith("skill_"):
                    connected_domains.add(self.graph.nodes[neighbor].get("domain", "Engineering"))

            bridges.append({
                "skill": lbl,
                "domain": domain,
                "bridge_score": round(score * 100, 1),
                "connected_domains_count": len(connected_domains),
                "connected_domains": list(connected_domains)
            })

        return bridges

    def export_d3_network(self, max_nodes: int = 160, min_cooccurrence_weight: int = 2) -> Dict[str, Any]:
        """Serialize graph for interactive HTML5 Canvas visualization.
        
        Guarantees that ALL uploaded candidate resumes are included in the graph.
        Connects them to their verified primary competency skills and cross-domain hubs.
        Filters out peripheral noise so the topology remains spacious, clean, and professional.
        """
        candidates = [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == "candidate"]
        # Sort candidates by score and degree
        candidates.sort(key=lambda c: (self.graph.nodes[c].get("score", 0), self.graph.degree(c)), reverse=True)
        
        # ALWAYS INCLUDE ALL CANDIDATES from uploaded resumes! None missing!
        selected_candidates = list(candidates)

        # Collect direct primary skills of selected candidates
        candidate_skills = set()
        for c in selected_candidates:
            for neighbor in self.graph.neighbors(c):
                if self.graph.nodes[neighbor].get("node_type") == "skill":
                    candidate_skills.add(neighbor)

        # Skills: prioritize direct verified skills of selected candidates, plus top hub skills
        skill_nodes = sorted(
            [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == "skill"],
            key=lambda x: (x in candidate_skills, self.graph.degree(x)),
            reverse=True
        )

        max_skills = max(45, max_nodes - len(selected_candidates))
        selected_skills = skill_nodes[:max_skills]
        selected_nodes = selected_candidates + selected_skills
        sub = self.graph.subgraph(selected_nodes)

        return self._serialize_subgraph(sub, min_cooccurrence_weight=min_cooccurrence_weight)

    def _serialize_subgraph(self, sub: nx.Graph, focus_id: Optional[str] = None, min_cooccurrence_weight: int = 1) -> Dict[str, Any]:
        """Convert a networkx graph into D3/Canvas compatible nodes and links arrays."""
        nodes = []
        node_map = {}

        total_sub_nodes = sub.number_of_nodes()
        deg_centrality = nx.degree_centrality(sub) if total_sub_nodes > 1 else {}

        for i, (n, d) in enumerate(sub.nodes(data=True)):
            ntype = d.get("node_type", "entity")
            label = d.get("label", n)
            score = d.get("score")
            decision = d.get("decision")
            stage = d.get("stage", "screened")
            domain = d.get("domain", "General")
            is_focus = (n == focus_id)
            deg = sub.degree(n)
            norm_deg_cent = round(deg_centrality.get(n, 0.0), 3)

            # Compute initials for candidate avatar
            initials = ""
            if ntype == "candidate":
                clean_name = label.replace("Dr. ", "").replace('"', '').strip()
                parts = [p for p in clean_name.split() if p and p[0].isalpha()]
                initials = "".join([p[0].upper() for p in parts[:2]]) or "CA"

            node_dict = {
                "id": n,
                "label": label,
                "type": ntype,
                "domain": domain,
                "degree": deg,
                "degree_centrality": norm_deg_cent,
                "is_focus": is_focus,
                "is_hub": (ntype == "skill" and deg >= 6)
            }
            if ntype == "candidate":
                node_dict["score"] = score or 0
                node_dict["decision"] = decision or "review"
                node_dict["stage"] = stage
                node_dict["initials"] = initials
                node_dict["domain"] = d.get("domain", "Core Engineering")
                node_dict["title"] = d.get("title", "")
                node_dict["email"] = d.get("email", "")
                node_dict["phone"] = d.get("phone", "")
                node_dict["experience_years"] = d.get("experience_years")
                node_dict["education"] = d.get("education", "")
                node_dict["summary"] = d.get("summary", "")
                node_dict["recruiter_memo"] = d.get("recruiter_memo", "")
                node_dict["integrity_score"] = d.get("integrity_score", 100)
                node_dict["semantic_fit"] = d.get("semantic_fit", 0.0)

                cand_id_raw = d.get("id") or n.replace("cand_", "")
                c_info = self.candidates_data.get(cand_id_raw, {})
                node_dict["all_skills"] = c_info.get("skills", [])

                # Candidate's direct skills in this subgraph for fast inspection
                cand_sub_skills = [
                    sub.nodes[nbr].get("label", nbr) for nbr in sub.neighbors(n)
                    if sub.nodes[nbr].get("node_type") == "skill"
                ]
                node_dict["verified_skills"] = cand_sub_skills
            elif ntype == "skill":
                # Candidates possessing this skill in this subgraph
                connected_cands = [
                    {
                        "id": sub.nodes[nbr].get("id", nbr.replace("cand_", "")),
                        "name": sub.nodes[nbr].get("label", nbr),
                        "score": sub.nodes[nbr].get("score", 0),
                        "decision": sub.nodes[nbr].get("decision", "review")
                    }
                    for nbr in sub.neighbors(n)
                    if sub.nodes[nbr].get("node_type") == "candidate"
                ]
                node_dict["connected_candidates"] = connected_cands[:8]

            nodes.append(node_dict)
            node_map[n] = i

        links = []
        for u, v, d in sub.edges(data=True):
            if u in node_map and v in node_map:
                rel = d.get("relation", "linked")
                w = float(d.get("weight", 1.0))
                if rel == "co_occurs" and w < min_cooccurrence_weight:
                    continue
                links.append({
                    "source": u,
                    "target": v,
                    "source_idx": node_map[u],
                    "target_idx": node_map[v],
                    "relation": rel,
                    "weight": w,
                    "is_cooccurrence": (rel == "co_occurs")
                })

        return {
            "nodes": nodes,
            "links": links,
            "node_count": len(nodes),
            "edge_count": len(links)
        }


# Singleton instance accessor
_GLOBAL_KNOWLEDGE_GRAPH: Optional[CandidateKnowledgeGraph] = None


def get_candidate_knowledge_graph(candidates: Optional[List[Dict[str, Any]]] = None) -> CandidateKnowledgeGraph:
    """Retrieve or build global CandidateKnowledgeGraph singleton."""
    global _GLOBAL_KNOWLEDGE_GRAPH
    if _GLOBAL_KNOWLEDGE_GRAPH is None or candidates is not None:
        if candidates is None:
            from storage import get_all_results
            candidates = get_all_results()
        _GLOBAL_KNOWLEDGE_GRAPH = CandidateKnowledgeGraph(candidates)
    return _GLOBAL_KNOWLEDGE_GRAPH


def refresh_knowledge_graph() -> CandidateKnowledgeGraph:
    """Force re-indexing of the Candidate Knowledge Graph from storage."""
    global _GLOBAL_KNOWLEDGE_GRAPH
    from storage import get_all_results
    candidates = get_all_results()
    _GLOBAL_KNOWLEDGE_GRAPH = CandidateKnowledgeGraph(candidates)
    return _GLOBAL_KNOWLEDGE_GRAPH
