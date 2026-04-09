from typing import Dict, Any, List
from src.domain.executors.base_executor import RuleExecutor
from src.domain.result_model import IssueItem
from src.domain.fact_model import NormalizedDataset
from src.crosscutting.ids.generator import generate_id
import dataclasses

class TopologyExecutor(RuleExecutor):
    def execute(self, rule_id: str, rule_def: Dict[str, Any], dataset: NormalizedDataset) -> List[IssueItem]:
        rule_subtype = rule_def.get("type")
        severity = rule_def.get("severity", "medium")
        issues = []
        
        if rule_subtype == "duplicate_link":
            # 识别重复连线
            seen_links = {}
            for i, link in enumerate(dataset.links):
                key = f"{link.src_device}:{link.src_port}->{link.dst_device}:{link.dst_port}"
                if key in seen_links:
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=f"Rule {rule_id} (duplicate_link) failed: Link {key} already exists.",
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
            # 识别缺失对端
            devices_map = {d.device_name for d in dataset.devices if d.device_name}
            for i, link in enumerate(dataset.links):
                missing_src = link.src_device not in devices_map
                missing_dst = link.dst_device not in devices_map
                
                if missing_src or missing_dst:
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=f"Rule {rule_id} (missing_peer) failed: Missing peer device in link {link.src_device}->{link.dst_device}.",
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
            assertion_type = rule_def.get("assertion_type")
            
            if assertion_type == "self_loop":
                for i, link in enumerate(dataset.links):
                    if link.src_device == link.dst_device:
                        issues.append(IssueItem(
                            issue_id=generate_id(),
                            message=f"Rule {rule_id} (topology_assertion) failed: Self-loop detected on {link.src_device}.",
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
                for link in dataset.links:
                    linked_devices.add(link.src_device)
                    linked_devices.add(link.dst_device)
                    
                for i, dev in enumerate(dataset.devices):
                    if dev.device_name and dev.device_name not in linked_devices:
                        issues.append(IssueItem(
                            issue_id=generate_id(),
                            message=f"Rule {rule_id} (topology_assertion) failed: Device {dev.device_name} is isolated.",
                            evidence={
                                "rule_id": rule_id,
                                "item_data": dataclasses.asdict(dev),
                                "device_name": dev.device_name
                            },
                            expected="Device has at least one link",
                            actual="No links found",
                            details={"target_type": "devices", "assertion_type": "isolated_device"},
                            source_row=i + 1,
                            severity=severity,
                            category="topology_assertion"
                        ))
        return issues
