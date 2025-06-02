#!/usr/bin/env python3
"""
Memory System Enhanced Capabilities - Persona evolution, self-reflection, and forgetting curve
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    psycopg2 = None
    RealDictCursor = None
    POSTGRES_AVAILABLE = False

from .core import MemorySystemBase


class EnhancedMemoryCapabilities(MemorySystemBase):
    """Handles enhanced AI memory capabilities like persona evolution, self-reflection, and forgetting curve."""
    
    def __init__(self, project_root: Optional[str] = None, embedding_model: str = "all-MiniLM-L6-v2"):
        super().__init__(project_root, embedding_model)

    # ========== PERSONA EVOLUTION LAYER ==========
    
    def store_persona_memory(
        self,
        persona_type: str,  # 'core_trait', 'preference', 'skill', 'weakness', 'goal'
        attribute_name: str,
        current_value: Union[str, Dict[str, Any]],
        confidence_score: float = 0.5,
        ai_instance_id: str = 'default',
        database_manager=None
    ) -> Dict[str, Any]:
        """Store or update AI persona characteristics for self-evolving identity."""
        if not POSTGRES_AVAILABLE or not database_manager or not database_manager.connection_pool:
            return {"success": False, "error": "PostgreSQL not available"}
        
        try:
            value_json = current_value if isinstance(current_value, dict) else {"value": current_value}
            
            # Check if this persona attribute already exists
            check_sql = """
            SELECT id, confidence_score, evidence_count, growth_trajectory
            FROM persona_memories 
            WHERE ai_instance_id = %s AND persona_type = %s AND attribute_name = %s;
            """
            
            with database_manager.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(check_sql, (ai_instance_id, persona_type, attribute_name))
                    
                    if existing := cur.fetchone():
                        # Update existing persona memory with growth tracking
                        old_trajectory = existing['growth_trajectory'] or []
                        new_trajectory = old_trajectory + [{
                            "timestamp": datetime.now().isoformat(),
                            "previous_value": existing.get('current_value'),
                            "new_value": value_json,
                            "confidence_change": confidence_score - existing['confidence_score']
                        }]
                        
                        update_sql = """
                        UPDATE persona_memories 
                        SET current_value = %s, 
                            confidence_score = %s,
                            evidence_count = evidence_count + 1,
                            last_updated = CURRENT_TIMESTAMP,
                            growth_trajectory = %s
                        WHERE id = %s
                        RETURNING id;
                        """
                        cur.execute(update_sql, (
                            self._safe_json(value_json),
                            confidence_score,
                            self._safe_json(new_trajectory),
                            existing['id']
                        ))
                        result_id = cur.fetchone()['id']
                        action = "updated"
                    else:
                        # Insert new persona memory
                        insert_sql = """
                        INSERT INTO persona_memories (
                            ai_instance_id, persona_type, attribute_name, 
                            current_value, confidence_score
                        ) VALUES (%s, %s, %s, %s, %s)
                        RETURNING id;
                        """
                        cur.execute(insert_sql, (
                            ai_instance_id, persona_type, attribute_name,
                            self._safe_json(value_json), confidence_score
                        ))
                        result_id = cur.fetchone()['id']
                        action = "created"
                
                conn.commit()
                database_manager.connection_pool.putconn(conn)
            
            self.logger.info(f"Persona memory {action}: {persona_type}.{attribute_name} = {current_value}")
            
            return {
                "success": True,
                "persona_id": result_id,
                "action": action,
                "ai_instance_id": ai_instance_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to store persona memory: {e}")
            return {"success": False, "error": str(e)}

    def get_current_persona(
        self, 
        ai_instance_id: str = 'default',
        persona_type: Optional[str] = None,
        min_confidence: float = 0.0,
        database_manager=None
    ) -> Dict[str, Any]:
        """Retrieve current AI persona for prompt context."""
        if not POSTGRES_AVAILABLE or not database_manager or not database_manager.connection_pool:
            return {"persona": "Basic AI Assistant (fallback mode)"}
        
        try:
            # Build SQL with optional filters
            where_conditions = ["ai_instance_id = %s"]
            params = [ai_instance_id]
            
            if persona_type:
                where_conditions.append("persona_type = %s")
                params.append(persona_type)
            
            if min_confidence > 0:
                where_conditions.append("confidence_score >= %s")
                params.append(min_confidence)
            
            persona_sql = f"""
            SELECT persona_type, attribute_name, current_value, confidence_score
            FROM persona_memories 
            WHERE {' AND '.join(where_conditions)}
            ORDER BY persona_type, confidence_score DESC;
            """
            
            with database_manager.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(persona_sql, params)
                    results = cur.fetchall()
                database_manager.connection_pool.putconn(conn)
            
            # Organize by persona type
            persona = {
                "core_traits": {},
                "preferences": {},
                "skills": {},
                "weaknesses": {},
                "goals": {},
                "ai_instance_id": ai_instance_id
            }
            
            for row in results:
                category = row['persona_type'] + 's'  # pluralize
                if category in persona:
                    persona[category][row['attribute_name']] = {
                        "value": row['current_value'],
                        "confidence": row['confidence_score']
                    }
            
            return persona
            
        except Exception as e:
            self.logger.error(f"Failed to get persona: {e}")
            return {"error": str(e)}

    def get_persona_evolution_summary(
        self, 
        days_back: int = 30, 
        persona_type: Optional[str] = None,
        database_manager=None
    ) -> Dict[str, Any]:
        """Get summary of how the AI persona has evolved over time."""
        if not POSTGRES_AVAILABLE or not database_manager or not database_manager.connection_pool:
            return {"error": "PostgreSQL not available"}
        
        try:
            evolution_sql, params = self._get_persona_evolution_sql_and_params(days_back, persona_type)
            
            with database_manager.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(evolution_sql, params)
                    results = cur.fetchall()
                database_manager.connection_pool.putconn(conn)
            
            # Analyze evolution patterns
            evolution_summary = {
                "analysis_period_days": days_back,
                "total_attributes_tracked": len(results),
                "persona_types": {},
                "confidence_trends": {},
                "recent_changes": []
            }
            
            # Group by persona type and analyze trends
            for row in results:
                p_type = row['persona_type']
                if p_type not in evolution_summary["persona_types"]:
                    evolution_summary["persona_types"][p_type] = {
                        "attributes": {},
                        "average_confidence": 0.0,
                        "total_attributes": 0
                    }
                
                attr_name = row['attribute_name']
                evolution_summary["persona_types"][p_type]["attributes"][attr_name] = {
                    "current_value": row['current_value'],
                    "confidence": row['confidence_score'],
                    "growth_trajectory": row['growth_trajectory'],
                    "last_updated": row['last_updated'].isoformat() if row['last_updated'] else None
                }
                
                # Track recent changes
                if row['last_updated'] and (datetime.now() - row['last_updated']).days <= 7:
                    evolution_summary["recent_changes"].append({
                        "type": p_type,
                        "attribute": attr_name,
                        "updated": row['last_updated'].isoformat(),
                        "confidence": row['confidence_score']
                    })
            
            # Calculate averages
            for p_type, data in evolution_summary["persona_types"].items():
                if data["attributes"]:
                    confidences = [attr["confidence"] for attr in data["attributes"].values()]
                    data["average_confidence"] = sum(confidences) / len(confidences)
                    data["total_attributes"] = len(data["attributes"])
            
            return evolution_summary
            
        except Exception as e:
            self.logger.error(f"Failed to get persona evolution summary: {e}")
            return {"error": str(e)}

    def _get_persona_evolution_sql_and_params(self, days_back: int, persona_type: Optional[str] = None):
        """Helper to get SQL and params for persona evolution summary."""
        if persona_type:
            evolution_sql = """
            SELECT 
                persona_type,
                attribute_name,
                current_value,
                confidence_score,
                growth_trajectory,
                first_observed,
                last_updated
            FROM persona_memories 
            WHERE first_observed >= CURRENT_TIMESTAMP - INTERVAL %s
                AND persona_type = %s
            ORDER BY persona_type, attribute_name, last_updated DESC;
            """
            params = (f"{days_back} days", persona_type)
        else:
            evolution_sql = """
            SELECT 
                persona_type,
                attribute_name,
                current_value,
                confidence_score,
                growth_trajectory,
                first_observed,
                last_updated
            FROM persona_memories 
            WHERE first_observed >= CURRENT_TIMESTAMP - INTERVAL %s
            ORDER BY persona_type, attribute_name, last_updated DESC;
            """
            params = (f"{days_back} days",)
        
        return evolution_sql, params

    # ========== REFLEXION CAPABILITY ==========
    
    def generate_self_reflection(
        self,
        reflection_trigger: str,
        situation_summary: str,
        what_went_well: Optional[str] = None,
        what_could_improve: Optional[str] = None,
        lessons_learned: Optional[str] = None,
        reflection_scope: str = 'interaction',
        database_manager=None
    ) -> Dict[str, Any]:
        """Generate and store self-reflection for continuous improvement (Reflexion capability)."""
        if not POSTGRES_AVAILABLE or not database_manager or not database_manager.connection_pool:
            return {"success": False, "error": "PostgreSQL not available"}
        
        try:
            # Default framework content if not provided
            reflection_content = {
                "what_went_well": what_went_well or "Framework ready for AI analysis",
                "what_could_improve": what_could_improve or "Framework ready for AI analysis", 
                "lessons_learned": lessons_learned or "Framework ready for AI analysis",
                "reflection_scope": reflection_scope
            }
            
            insert_sql = """
            INSERT INTO self_reflections (
                session_id, project_id, reflection_trigger, situation_summary,
                what_went_well, what_could_improve, lessons_learned, confidence_in_analysis
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at;
            """
            
            with database_manager.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(insert_sql, (
                        self.session_id,
                        self.current_project_id,
                        reflection_trigger,
                        situation_summary,
                        reflection_content["what_went_well"],
                        reflection_content["what_could_improve"],
                        reflection_content["lessons_learned"],
                        0.5  # Medium confidence until AI enhancement
                    ))
                    result = cur.fetchone()
                conn.commit()
                database_manager.connection_pool.putconn(conn)
            
            self.logger.info(f"Self-reflection stored: {reflection_trigger} - {situation_summary[:50]}...")
            
            return {
                "success": True,
                "reflection_id": result['id'],
                "created_at": result['created_at'].isoformat(),
                "trigger": reflection_trigger,
                "content": reflection_content,
                "note": "Framework ready - can be enhanced with LLM analysis"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate reflection: {e}")
            return {"success": False, "error": str(e)}

    # ========== FORGETTING CURVE MECHANISM ==========
    
    def apply_forgetting_curve(
        self,
        days_threshold: int = 7,
        access_threshold: int = 1,
        dry_run: bool = False,
        database_manager=None
    ) -> Dict[str, Any]:
        """Apply forgetting curve algorithm to decay old or unused memories."""
        if not POSTGRES_AVAILABLE or not database_manager or not database_manager.connection_pool:
            return {"success": False, "error": "PostgreSQL not available"}
        
        try:
            # Find memories eligible for decay
            decay_candidates_sql = """
            SELECT 
                m.id, m.importance_score, m.created_at, m.title,
                COALESCE(mal.access_count, 0) as access_count,
                COALESCE(mal.last_accessed, m.created_at) as last_accessed
            FROM memories m
            LEFT JOIN memory_access_log mal ON m.id = mal.memory_id
            WHERE m.created_at < CURRENT_TIMESTAMP - INTERVAL %s
              AND COALESCE(mal.access_count, 0) <= %s
              AND m.importance_score > 0.1
            ORDER BY m.importance_score ASC, m.created_at ASC;
            """
            
            with database_manager.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(decay_candidates_sql, (f"{days_threshold} days", access_threshold))
                    candidates = cur.fetchall()
                database_manager.connection_pool.putconn(conn)
            
            if not candidates:
                return {
                    "success": True,
                    "affected_memories": 0,
                    "message": "No memories eligible for decay"
                }
            
            # Apply forgetting curve algorithm
            affected_memories = []
            
            for memory in candidates:
                age_days = (datetime.now() - memory['created_at']).days
                access_count = memory['access_count']
                current_importance = memory['importance_score']
                
                # Ebbinghaus-inspired decay formula
                # Base decay increases with age, reduced by access frequency
                base_decay = min(0.1 * (age_days / 7.0), 0.8)  # Max 80% decay
                access_protection = min(0.2 * access_count, 0.5)  # Max 50% protection
                final_decay = max(0, base_decay - access_protection)
                
                new_importance = max(0.05, current_importance * (1 - final_decay))
                
                if new_importance != current_importance:
                    affected_memories.append({
                        "id": memory['id'],
                        "title": memory['title'],
                        "old_importance": current_importance,
                        "new_importance": new_importance,
                        "decay_amount": final_decay,
                        "age_days": age_days,
                        "access_count": access_count
                    })
            
            # Apply changes if not dry run
            if not dry_run and affected_memories:
                with database_manager.connection_pool.getconn() as conn:
                    with conn.cursor() as cur:
                        for memory in affected_memories:
                            cur.execute(
                                "UPDATE memories SET importance_score = %s WHERE id = %s",
                                (memory['new_importance'], memory['id'])
                            )
                    conn.commit()
                    database_manager.connection_pool.putconn(conn)
                
                self.logger.info(f"Applied forgetting curve to {len(affected_memories)} memories")
            
            return {
                "success": True,
                "affected_memories": len(affected_memories),
                "dry_run": dry_run,
                "decay_details": affected_memories[:10],  # Return first 10 for inspection
                "algorithm": {
                    "days_threshold": days_threshold,
                    "access_threshold": access_threshold,
                    "base_decay_rate": "0.1 per week",
                    "max_decay": "80%",
                    "access_protection": "up to 50%"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to apply forgetting curve: {e}")
            return {"success": False, "error": str(e)}

    def log_memory_access(
        self, 
        memory_ids: List[int], 
        access_context: str, 
        relevance_score: float = 0.5,
        database_manager=None
    ) -> None:
        """Log memory access for forgetting algorithm."""
        if not POSTGRES_AVAILABLE or not database_manager or not database_manager.connection_pool:
            return
        
        try:
            with database_manager.connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    for memory_id in memory_ids:
                        # Insert or update access log
                        cur.execute("""
                        INSERT INTO memory_access_log (memory_id, access_count, last_accessed, access_context, relevance_score)
                        VALUES (%s, 1, CURRENT_TIMESTAMP, %s, %s)
                        ON CONFLICT (memory_id) 
                        DO UPDATE SET 
                            access_count = memory_access_log.access_count + 1,
                            last_accessed = CURRENT_TIMESTAMP,
                            access_context = %s,
                            relevance_score = %s;
                        """, (memory_id, access_context, relevance_score, access_context, relevance_score))
                conn.commit()
                database_manager.connection_pool.putconn(conn)
                
        except Exception as e:
            self.logger.warning(f"Failed to log memory access: {e}")

    # ========== EMOTIONAL INTELLIGENCE ==========
    
    def reflect_on_interaction(
        self,
        reflection_type: str,
        content: Dict[str, Any],
        mood_score: Optional[float] = None,
        database_manager=None
    ) -> Dict[str, Any]:
        """Store an emotional reflection about an interaction."""
        if not POSTGRES_AVAILABLE or not database_manager or not database_manager.connection_pool:
            return {"success": False, "error": "PostgreSQL not available"}
        
        try:
            insert_sql = """
            INSERT INTO emotional_reflections (
                session_id, project_id, reflection_type, content, mood_score
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id, created_at;
            """
            
            with database_manager.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(insert_sql, (
                        self.session_id,
                        self.current_project_id,
                        reflection_type,
                        self._safe_json(content),
                        mood_score
                    ))
                    result = cur.fetchone()
                conn.commit()
                database_manager.connection_pool.putconn(conn)
            
            self.logger.info(f"Stored emotional reflection: {reflection_type}")
            
            return {
                "success": True,
                "reflection_id": result['id'],
                "created_at": result['created_at'].isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to store reflection: {e}")
            return {"success": False, "error": str(e)}

    def get_emotional_insights(
        self, 
        days_back: int = 30,
        database_manager=None
    ) -> Dict[str, Any]:
        """Get emotional insights and patterns from recent interactions."""
        if not POSTGRES_AVAILABLE or not database_manager or not database_manager.connection_pool:
            return {"insights": "Emotional insights not available without PostgreSQL"}
        
        try:
            insights_sql = """
            SELECT 
                reflection_type, 
                mood_score, 
                content,
                created_at
            FROM emotional_reflections 
            WHERE project_id = %s 
              AND created_at >= CURRENT_TIMESTAMP - INTERVAL %s
            ORDER BY created_at DESC;
            """
            
            with database_manager.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(insights_sql, (self.current_project_id, f"{days_back} days"))
                    reflections = cur.fetchall()
                database_manager.connection_pool.putconn(conn)
            
            if not reflections:
                return {"insights": "No emotional reflections found for this period"}
            
            # Analyze patterns
            mood_scores = [r['mood_score'] for r in reflections if r['mood_score'] is not None]
            reflection_types = {}
            
            for reflection in reflections:
                r_type = reflection['reflection_type']
                reflection_types[r_type] = reflection_types.get(r_type, 0) + 1
            
            insights = {
                "period_days": days_back,
                "total_reflections": len(reflections),
                "mood_analysis": {
                    "average_mood": sum(mood_scores) / len(mood_scores) if mood_scores else None,
                    "mood_range": {
                        "min": min(mood_scores) if mood_scores else None,
                        "max": max(mood_scores) if mood_scores else None
                    },
                    "total_mood_entries": len(mood_scores)
                },
                "reflection_types": reflection_types,
                "recent_reflections": [
                    {
                        "type": r['reflection_type'],
                        "mood": r['mood_score'],
                        "date": r['created_at'].isoformat(),
                        "content_summary": str(r['content'])[:100] + "..." if len(str(r['content'])) > 100 else str(r['content'])
                    }
                    for r in reflections[:5]
                ]
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to get emotional insights: {e}")
            return {"error": str(e)}
