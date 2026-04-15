from typing import Dict, Any, List
from src.domain.executors.base_executor import RuleExecutor
from src.domain.result_model import IssueItem
from src.domain.compiled_rule_schema import CompiledRule
from src.crosscutting.ids.generator import generate_id
from src.crosscutting.logging.logger import get_logger
import dataclasses

logger = get_logger(__name__)

class TopologyExecutor(RuleExecutor):
    def execute(self, *args) -> List[IssueItem]:
        if len(args) == 3:
            compiled_rule, dataset, context = args
        elif len(args) == 4:
            _, compiled_rule, dataset, context = args
        else:
            raise TypeError("execute() expects (compiled_rule, dataset, context) or (rule_id, compiled_rule, dataset, context)")
        rule_id = compiled_rule.rule_id
        params = compiled_rule.params or {}
        extra_type = compiled_rule.get("type") if hasattr(compiled_rule, "get") else None
        rule_subtype = params.get("type") or extra_type or getattr(compiled_rule, "type", None) or compiled_rule.rule_type

        msg = compiled_rule.message
        severity = msg.severity if hasattr(msg, "severity") else (getattr(compiled_rule, "severity", None) or msg.get("severity", "medium"))
        msg_template = msg.template if hasattr(msg, "template") else msg.get("template", "")
        use_template_verbatim = hasattr(msg, "template") and bool(msg_template)
        issues = []
        
        links = dataset.get("links", [])
        devices = dataset.get("devices", [])
        
        if rule_subtype == "duplicate_link":
            seen_links = {}
            for i, link in enumerate(links):
                key = f"{link.src_device}:{link.src_port}->{link.dst_device}:{link.dst_port}"
                if key in seen_links:
                    if use_template_verbatim:
                        msg = msg_template
                    else:
                        prefix = (msg_template + " ") if msg_template else ""
                        msg = f"{prefix}Rule {rule_id} (duplicate_link) failed: Link {key} already exists."
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=msg,
                        evidence={
                            "rule_id": rule_id,
                            "item_data": dataclasses.asdict(link),
                            "source_device": link.src_device,
                            "target_device": link.dst_device
                        },
                        expected="Unique Link",
                        actual=key,
                        details={"target_type": "links"},
                        source_row=i + 1,
                        severity=severity,
                        category="duplicate_link"
                    ))
                else:
                    seen_links[key] = i
                    
        elif rule_subtype == "missing_peer":
            devices_map = {d.device_name for d in devices if d.device_name}
            for i, link in enumerate(links):
                missing_src = link.src_device not in devices_map
                missing_dst = link.dst_device not in devices_map
                
                if missing_src or missing_dst:
                    if use_template_verbatim:
                        msg = msg_template
                    else:
                        prefix = (msg_template + " ") if msg_template else ""
                        msg = f"{prefix}Rule {rule_id} (missing_peer) failed: Missing peer device in link {link.src_device}->{link.dst_device}."
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=msg,
                        evidence={
                            "rule_id": rule_id,
                            "item_data": dataclasses.asdict(link),
                            "source_device": link.src_device,
                            "target_device": link.dst_device
                        },
                        expected="Both peers exist",
                        actual=f"Src missing: {missing_src}, Dst missing: {missing_dst}",
                        details={"target_type": "links"},
                        source_row=i + 1,
                        severity=severity,
                        category="missing_peer"
                    ))
                    
        elif rule_subtype == "topology_assertion":
            extra_assertion_type = compiled_rule.get("assertion_type") if hasattr(compiled_rule, "get") else None
            assertion_type = params.get("assertion_type") or extra_assertion_type or getattr(compiled_rule, "assertion_type", "")
            
            if assertion_type == "self_loop":
                for i, link in enumerate(links):
                    if link.src_device == link.dst_device:
                        if use_template_verbatim:
                            msg = msg_template
                        else:
                            prefix = (msg_template + " ") if msg_template else ""
                            msg = f"{prefix}Rule {rule_id} (topology_assertion) failed: Self-loop detected on {link.src_device}."
                        issues.append(IssueItem(
                            issue_id=generate_id(),
                            message=msg,
                            evidence={
                                "rule_id": rule_id,
                                "item_data": dataclasses.asdict(link),
                                "source_device": link.src_device,
                                "target_device": link.dst_device
                            },
                            expected="Different source and target devices",
                            actual="Same source and target device",
                            details={"target_type": "links", "assertion_type": "self_loop"},
                            source_row=i + 1,
                            severity=severity,
                            category="topology_assertion"
                        ))
                        
            elif assertion_type == "isolated_device":
                linked_devices = set()
                for link in links:
                    linked_devices.add(link.src_device)
                    linked_devices.add(link.dst_device)
                    
                for i, dev in enumerate(devices):
                    if dev.device_name and dev.device_name not in linked_devices:
                        if use_template_verbatim:
                            msg = msg_template
                        else:
                            prefix = (msg_template + " ") if msg_template else ""
                            msg = f"{prefix}Rule {rule_id} (topology_assertion) failed: Device {dev.device_name} is isolated."
                        issues.append(IssueItem(
                            issue_id=generate_id(),
                            message=msg,
                            evidence={
                                "rule_id": rule_id,
                                "item_data": dataclasses.asdict(dev),
                                "device_name": dev.device_name
                            },
                            expected="Device has links",
                            actual="No links found",
                            details={"target_type": "devices", "assertion_type": "isolated_device"},
                            source_row=i + 1,
                            severity=severity,
                            category="topology_assertion"
                        ))
        return issues
