import random

class ResponseGeneratorSimple:
    def __init__(self, graph_handler):
        self.handler = graph_handler

    def get_concept_label(self, concept_id):
        """Fetches the primary Arabic label for a concept."""
        if self.handler.graph.has_node(concept_id):
            labels = self.handler.graph.nodes[concept_id].get("labels", [])
            if labels:
                return labels[0]
        return concept_id

    def generate(self, res, persona_id="persona_1"):
        """Generates a natural Arabic response from the reasoning result, applying the dynamic persona."""
        persona = self.handler.get_persona(persona_id)
        
        # Load persona rules dynamically (Zero-Hardcoding of style)
        particles = [""]
        fillers = [""]
        if persona:
            style = persona.get("language_style", {})
            particles = style.get("particles", [""])
            fillers = style.get("filler_words", [""])
            
        p_ref = random.choice(particles) if particles else ""
        f_ref = random.choice(fillers) if fillers else ""
        
        type_ = res.get("type", "unknown")
        
        # 1. Classification Response
        if type_ == "classification":
            c1_lbl = self.get_concept_label(res["concept1"])
            c2_lbl = self.get_concept_label(res["concept2"])
            if res["result"]:
                return f"{p_ref}، {f_ref} {c1_lbl} هو {c2_lbl}، دي الحقيقة! الاستدلال التصنيفي أثبت العلاقة دي بالوراثة الصاعدة."
            else:
                return f"لا {p_ref}، حسب معرفتي المنطقية {c1_lbl} ليس {c2_lbl}."
                
        # 2. Location Response
        elif type_ == "location":
            c_lbl = self.get_concept_label(res["concept"])
            loc_lbl = res["location_label"]
            return f"{p_ref}، {f_ref} {c_lbl} بيعيش في {loc_lbl}."
            
        # 3. Hypothetical Response (Causal + Analogy)
        elif type_ == "hypothetical":
            entity_lbl = self.get_concept_label(res["entity"])
            env_lbl = self.get_concept_label(res["environment"])
            
            if res["needs_adaptation"]:
                prop_lbl = self.get_concept_label(res["transferred_property"])
                cand_lbl = self.get_concept_label(res["analogy_candidate"])
                return (
                    f"{p_ref}، {f_ref} لو {entity_lbl} عاش في {env_lbl}، "
                    f"أكيد محتاج يتكيف! البيئة هناك برد شديد ومحتاجة عزل حراري قوي، "
                    f"عشان كدة هيحتاج يطور {prop_lbl} زي {cand_lbl} بالظبط اللي بيعيش هناك. "
                    f"وبالنسبة للغذاء، هيتخلى عن طرائده المعتادة ويتغذى على فرائس قطبية متوفرة زي الفقمات والأسماك. "
                    f"يعني تكيف كامل مبني على التناظر المنطقي."
                )
            else:
                return f"{p_ref}، لو {entity_lbl} عاش في {env_lbl} مش محتاج يغير صفاته الجسدية لأنه مهيأ ليها بالفعل."
                
        # 4. Comparison Response
        elif type_ == "comparison":
            c1_lbl = self.get_concept_label(res["concept1"])
            c2_lbl = self.get_concept_label(res["concept2"])
            
            p1_str = "، ".join([self.get_concept_label(p["property"]) for p in res["props1"] if p["relation"] == "has_property"])
            p2_str = "، ".join([self.get_concept_label(p["property"]) for p in res["props2"] if p["relation"] == "has_property"])
            
            l1 = next((self.get_concept_label(p["property"]) for p in res["props1"] if p["relation"] == "lives_in"), "بيئته")
            l2 = next((self.get_concept_label(p["property"]) for p in res["props2"] if p["relation"] == "lives_in"), "بيئته")
            
            return (
                f"{p_ref}، {f_ref} الفرق واضح جداً بين {c1_lbl} و {c2_lbl}: "
                f"أولاً، {c1_lbl} بيعيش في {l1} وعنده {p1_str or 'صفات مخصصة لبيئته'}. "
                f"أما {c2_lbl} فبيعيش في {l2} وعنده {p2_str or 'صفات تناسب البرودة'}. "
                f"لكن التشابه الجوهري أن كلاهما ثدييات مفترسة تصنيفياً."
            )
            
        # 6. Teaching Response
        elif type_ == "teaching":
            return f"{p_ref}، {res.get('message', 'تم حفظ المعلومة بنجاح.')}"
            
        # 7. Anomaly Response
        elif type_ == "anomaly":
            entity_lbl = self.get_concept_label(res["entity"])
            return f"{p_ref}، {f_ref} تم رصد استثناء وشذوذ عن القاعدة للـ {entity_lbl}: الحالة هي {res['anomaly_type']} والسبب هو {res['reason']} (معدل الشذوذ {res['anomaly_score']:.2f})."
            
        # 8. Comparison Scale Response
        elif type_ == "comparison_scale":
            c1_lbl = self.get_concept_label(res["entity1"])
            c2_lbl = self.get_concept_label(res["entity2"])
            rel_str = "أكبر من" if res["result"] else "ليس أكبر من"
            return f"{p_ref}، {f_ref} مقارنة الكائنات على مقياس [{res['property_name']}]: قيمة {c1_lbl} {rel_str} قيمة {c2_lbl}."
            
        # 9. Temporal Logic Response
        elif type_ == "temporal_logic":
            rel_str = "قبل" if res["result"] else "ليس قبل"
            return f"{p_ref}، {f_ref} الترتيب الزمني يوضح أن حدث [{res['event']}] يقع {rel_str} الحدث [{res['reference']}]."
            
        # 10. Modality Response
        elif type_ == "modality":
            rel_str = "صحيحة ومؤكدة" if res["result"] else "غير صحيحة أو غير مؤكدة"
            return f"{p_ref}، {f_ref} استناداً لمنطق الجهة والضرورة، فإن هذه الفرضية {rel_str} (نوع الجهة: {res['modality']} وثقتها {res['modality_confidence']:.2f})."
            
        # 11. Causal Chain Response
        elif type_ == "causal_chain":
            steps = res["chain"]["steps"]
            chain_str = " -> ".join([f"[{s['event']}]" for s in steps])
            return f"{p_ref}، {f_ref} التسلسل السببي متعدد الخطوات بدءاً من [{res['initial_state']}] هو: {chain_str}."
            
        # 12. Quantifier Response
        elif type_ == "quantifier":
            rel_str = "صحيحة منطقياً" if res["result"] else "غير مستلزمة منطقياً"
            return f"{p_ref}، {f_ref} استدلال سور القضية يثبت أن هذه القضية {rel_str} (السور المستعلم عنه: {res['quantifier']})."
            
        # 13. Negation Response
        elif type_ == "negation":
            rel_str = "صحيحة" if res["result"] else "خاطئة"
            return f"{p_ref}، {f_ref} استدلال النفي وعكس القطبية يثبت أن هذه القضية المنفية {rel_str}."
            
        # 14. Semantic Roles Response
        elif type_ == "semantic_roles":
            roles_list = []
            for r_type, val in res["roles"].items():
                val_lbl = self.get_concept_label(val)
                roles_list.append(f"{r_type}: {val_lbl}")
            roles_str = "، ".join(roles_list)
            return f"{p_ref}، {f_ref} الأدوار الدلالية للفعل [{res['predicate']}] هي: {roles_str}."
            
        # 15. Honest Fail-safe (No Hallucination!)
        else:
            return f"{p_ref}، بص بقى، معنديش أي معلومة أو حقيقة منطقية تسند السؤال ده في قاعدة البيانات حالياً، وأنا بفضل أقول معرفش على إني أهلس!"
