"""
Rules and constraints utility classes

Manages blendshape rules, cross-module exclusions, and weight constraints
for the Hair QC Tool system.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json


class ConstraintType(Enum):
    """Types of blendshape constraints"""
    EXCLUSION = "exclusion"          # Binary on/off - blendshapes cannot be used together
    WEIGHT_LIMIT = "weight_limit"    # Maximum weight when used together
    DEPENDENCY = "dependency"        # One blendshape triggers another


@dataclass
class BlendshapeRule:
    """Individual blendshape rule definition"""
    rule_id: str
    rule_type: ConstraintType
    source_module: str
    source_blendshape: str
    target_module: str
    target_blendshape: str
    constraint_value: float = 1.0  # Max weight or dependency strength
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['rule_type'] = self.rule_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BlendshapeRule':
        """Create from dictionary"""
        data = data.copy()
        data['rule_type'] = ConstraintType(data['rule_type'])
        return cls(**data)


class BlendshapeRulesManager:
    """Manages blendshape rules and constraints"""
    
    def __init__(self):
        self.rules: Dict[str, BlendshapeRule] = {}
        self.internal_exclusions: Dict[str, List[str]] = {}  # module -> excluded blendshapes
    
    def add_rule(self, rule: BlendshapeRule) -> bool:
        """Add a blendshape rule"""
        try:
            self.rules[rule.rule_id] = rule
            return True
        except Exception as e:
            print(f"[Rules Manager] Error adding rule: {e}")
            return False
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a blendshape rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[BlendshapeRule]:
        """Get a specific rule"""
        return self.rules.get(rule_id)
    
    def get_rules_for_blendshape(self, module: str, blendshape: str) -> List[BlendshapeRule]:
        """Get all rules that affect a specific blendshape"""
        matching_rules = []
        for rule in self.rules.values():
            if ((rule.source_module == module and rule.source_blendshape == blendshape) or
                (rule.target_module == module and rule.target_blendshape == blendshape)):
                matching_rules.append(rule)
        return matching_rules
    
    def get_exclusion_rules(self) -> List[BlendshapeRule]:
        """Get all exclusion rules"""
        return [rule for rule in self.rules.values() if rule.rule_type == ConstraintType.EXCLUSION]
    
    def get_weight_limit_rules(self) -> List[BlendshapeRule]:
        """Get all weight limit rules"""
        return [rule for rule in self.rules.values() if rule.rule_type == ConstraintType.WEIGHT_LIMIT]
    
    def get_dependency_rules(self) -> List[BlendshapeRule]:
        """Get all dependency rules"""
        return [rule for rule in self.rules.values() if rule.rule_type == ConstraintType.DEPENDENCY]
    
    def create_exclusion_rule(self, source_module: str, source_blendshape: str,
                            target_module: str, target_blendshape: str,
                            description: str = "") -> BlendshapeRule:
        """Create a new exclusion rule"""
        rule_id = f"{source_module}.{source_blendshape}_X_{target_module}.{target_blendshape}"
        
        rule = BlendshapeRule(
            rule_id=rule_id,
            rule_type=ConstraintType.EXCLUSION,
            source_module=source_module,
            source_blendshape=source_blendshape,
            target_module=target_module,
            target_blendshape=target_blendshape,
            constraint_value=0.0,  # Exclusion = 0 weight allowed
            description=description or f"Exclude {source_module}.{source_blendshape} with {target_module}.{target_blendshape}"
        )
        
        self.add_rule(rule)
        return rule
    
    def create_weight_limit_rule(self, source_module: str, source_blendshape: str,
                               target_module: str, target_blendshape: str,
                               max_weight: float, description: str = "") -> BlendshapeRule:
        """Create a new weight limit rule"""
        rule_id = f"{source_module}.{source_blendshape}_W_{target_module}.{target_blendshape}_{max_weight}"
        
        rule = BlendshapeRule(
            rule_id=rule_id,
            rule_type=ConstraintType.WEIGHT_LIMIT,
            source_module=source_module,
            source_blendshape=source_blendshape,
            target_module=target_module,
            target_blendshape=target_blendshape,
            constraint_value=max_weight,
            description=description or f"Limit {target_module}.{target_blendshape} to {max_weight} when {source_module}.{source_blendshape} active"
        )
        
        self.add_rule(rule)
        return rule
    
    def create_dependency_rule(self, source_module: str, source_blendshape: str,
                             target_module: str, target_blendshape: str,
                             strength: float = 1.0, description: str = "") -> BlendshapeRule:
        """Create a new dependency rule (one blendshape triggers another)"""
        rule_id = f"{source_module}.{source_blendshape}_D_{target_module}.{target_blendshape}"
        
        rule = BlendshapeRule(
            rule_id=rule_id,
            rule_type=ConstraintType.DEPENDENCY,
            source_module=source_module,
            source_blendshape=source_blendshape,
            target_module=target_module,
            target_blendshape=target_blendshape,
            constraint_value=strength,
            description=description or f"{source_module}.{source_blendshape} triggers {target_module}.{target_blendshape}"
        )
        
        self.add_rule(rule)
        return rule
    
    def set_internal_exclusions(self, module: str, exclusions: List[str]):
        """Set internal exclusions for a module"""
        self.internal_exclusions[module] = exclusions
    
    def get_internal_exclusions(self, module: str) -> List[str]:
        """Get internal exclusions for a module"""
        return self.internal_exclusions.get(module, [])
    
    def is_combination_valid(self, active_blendshapes: Dict[str, Dict[str, float]]) -> Tuple[bool, List[str]]:
        """
        Check if a combination of blendshapes is valid according to rules
        
        Args:
            active_blendshapes: {module: {blendshape: weight}}
        
        Returns:
            (is_valid, list_of_violations)
        """
        violations = []
        
        # Check exclusion rules
        for rule in self.get_exclusion_rules():
            source_weight = active_blendshapes.get(rule.source_module, {}).get(rule.source_blendshape, 0.0)
            target_weight = active_blendshapes.get(rule.target_module, {}).get(rule.target_blendshape, 0.0)
            
            if source_weight > 0 and target_weight > 0:
                violations.append(f"Exclusion violation: {rule.source_module}.{rule.source_blendshape} cannot be used with {rule.target_module}.{rule.target_blendshape}")
        
        # Check weight limit rules
        for rule in self.get_weight_limit_rules():
            source_weight = active_blendshapes.get(rule.source_module, {}).get(rule.source_blendshape, 0.0)
            target_weight = active_blendshapes.get(rule.target_module, {}).get(rule.target_blendshape, 0.0)
            
            if source_weight > 0 and target_weight > rule.constraint_value:
                violations.append(f"Weight limit violation: {rule.target_module}.{rule.target_blendshape} weight {target_weight} exceeds limit {rule.constraint_value} when {rule.source_module}.{rule.source_blendshape} is active")
        
        # Check internal exclusions
        for module, exclusions in self.internal_exclusions.items():
            if module in active_blendshapes:
                active_in_module = [bs for bs, weight in active_blendshapes[module].items() if weight > 0]
                
                # Check if any excluded blendshapes are both active
                for i, bs1 in enumerate(active_in_module):
                    for bs2 in active_in_module[i+1:]:
                        if bs1 in exclusions and bs2 in exclusions:
                            violations.append(f"Internal exclusion violation in {module}: {bs1} cannot be used with {bs2}")
        
        return len(violations) == 0, violations
    
    def apply_constraints_to_combination(self, active_blendshapes: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """
        Apply weight constraints to a blendshape combination
        
        Args:
            active_blendshapes: {module: {blendshape: weight}}
        
        Returns:
            Constrained blendshape weights
        """
        constrained = active_blendshapes.copy()
        
        # Apply weight limit rules
        for rule in self.get_weight_limit_rules():
            source_weight = constrained.get(rule.source_module, {}).get(rule.source_blendshape, 0.0)
            
            if source_weight > 0:
                # Limit target weight
                if rule.target_module in constrained and rule.target_blendshape in constrained[rule.target_module]:
                    current_weight = constrained[rule.target_module][rule.target_blendshape]
                    if current_weight > rule.constraint_value:
                        constrained[rule.target_module][rule.target_blendshape] = rule.constraint_value
        
        # Apply dependency rules
        for rule in self.get_dependency_rules():
            source_weight = constrained.get(rule.source_module, {}).get(rule.source_blendshape, 0.0)
            
            if source_weight > 0:
                # Activate target blendshape
                if rule.target_module not in constrained:
                    constrained[rule.target_module] = {}
                
                # Set dependency weight (source_weight * strength)
                dependency_weight = source_weight * rule.constraint_value
                constrained[rule.target_module][rule.target_blendshape] = dependency_weight
        
        return constrained
    
    def to_dict(self) -> Dict[str, Any]:
        """Export all rules to dictionary"""
        return {
            "rules": {rule_id: rule.to_dict() for rule_id, rule in self.rules.items()},
            "internal_exclusions": self.internal_exclusions
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Import rules from dictionary"""
        self.rules = {}
        self.internal_exclusions = data.get("internal_exclusions", {})
        
        for rule_id, rule_data in data.get("rules", {}).items():
            try:
                rule = BlendshapeRule.from_dict(rule_data)
                self.rules[rule_id] = rule
            except Exception as e:
                print(f"[Rules Manager] Error loading rule {rule_id}: {e}")
    
    def to_json(self) -> str:
        """Export rules to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    def from_json(self, json_str: str):
        """Import rules from JSON string"""
        try:
            data = json.loads(json_str)
            self.from_dict(data)
        except json.JSONDecodeError as e:
            print(f"[Rules Manager] Error parsing JSON: {e}")


class CombinationGenerator:
    """Generates valid blendshape combinations based on rules"""
    
    def __init__(self, rules_manager: BlendshapeRulesManager):
        self.rules_manager = rules_manager
    
    def generate_combinations(self, module_blendshapes: Dict[str, List[str]], 
                            max_combinations: int = 1000) -> List[Dict[str, Dict[str, float]]]:
        """
        Generate valid blendshape combinations
        
        Args:
            module_blendshapes: {module: [blendshape_names]}
            max_combinations: Maximum number of combinations to generate
        
        Returns:
            List of valid combinations: [{module: {blendshape: weight}}]
        """
        from itertools import product
        
        valid_combinations = []
        
        # Generate all possible on/off combinations first
        all_blendshapes = []
        module_mapping = {}
        
        for module, blendshapes in module_blendshapes.items():
            for blendshape in blendshapes:
                all_blendshapes.append((module, blendshape))
                module_mapping[(module, blendshape)] = len(all_blendshapes) - 1
        
        # Generate combinations (on/off for each blendshape)
        combination_count = 0
        
        # Start with simpler combinations (fewer active blendshapes)
        for num_active in range(1, min(len(all_blendshapes) + 1, 6)):  # Limit to 5 active max for performance
            if combination_count >= max_combinations:
                break
            
            from itertools import combinations
            
            for active_indices in combinations(range(len(all_blendshapes)), num_active):
                if combination_count >= max_combinations:
                    break
                
                # Create combination with default weights
                combination = {}
                for idx in active_indices:
                    module, blendshape = all_blendshapes[idx]
                    if module not in combination:
                        combination[module] = {}
                    combination[module][blendshape] = 1.0  # Default full weight
                
                # Check if combination is valid
                is_valid, violations = self.rules_manager.is_combination_valid(combination)
                
                if is_valid:
                    # Apply constraints to get final weights
                    constrained_combination = self.rules_manager.apply_constraints_to_combination(combination)
                    valid_combinations.append(constrained_combination)
                    combination_count += 1
        
        return valid_combinations
    
    def generate_timeline_data(self, combinations: List[Dict[str, Dict[str, float]]], 
                             frames_per_combination: int = 10) -> Dict[str, Any]:
        """
        Generate timeline animation data from combinations
        
        Args:
            combinations: List of blendshape combinations
            frames_per_combination: Number of frames per combination
        
        Returns:
            Animation data dictionary
        """
        timeline_data = {
            "frame_rate": 24,
            "total_frames": len(combinations) * frames_per_combination,
            "frames_per_combination": frames_per_combination,
            "combinations": [],
            "keyframes": {}
        }
        
        current_frame = 1
        
        for i, combination in enumerate(combinations):
            start_frame = current_frame
            end_frame = current_frame + frames_per_combination - 1
            
            combination_data = {
                "index": i,
                "start_frame": start_frame,
                "end_frame": end_frame,
                "blendshapes": combination
            }
            
            timeline_data["combinations"].append(combination_data)
            
            # Create keyframes for this combination
            for module, blendshapes in combination.items():
                if module not in timeline_data["keyframes"]:
                    timeline_data["keyframes"][module] = {}
                
                for blendshape, weight in blendshapes.items():
                    if blendshape not in timeline_data["keyframes"][module]:
                        timeline_data["keyframes"][module][blendshape] = []
                    
                    # Add keyframes: start with weight, end with weight, next starts with 0
                    timeline_data["keyframes"][module][blendshape].extend([
                        {"frame": start_frame, "weight": weight},
                        {"frame": end_frame, "weight": weight}
                    ])
                    
                    # Add transition to 0 for next combination (if not last)
                    if i < len(combinations) - 1:
                        timeline_data["keyframes"][module][blendshape].append({
                            "frame": end_frame + 1, "weight": 0.0
                        })
            
            current_frame = end_frame + 1
        
        return timeline_data