from typing import Dict, Any, List

class NormalizationService:
    """
    Converts raw excel row data into normalized Domain Facts:
    DeviceFact, PortFact, LinkFact
    """
    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        dataset = {
            "devices": [],
            "ports": [],
            "links": []
        }
        
        # Simple heuristic normalization based on sheet names or headers
        for sheet_name, rows in raw_data.items():
            s_name = sheet_name.lower()
            if "device" in s_name:
                for r in rows:
                    dataset["devices"].append({
                        "fact_type": "DeviceFact",
                        "device_name": r.get("Device Name", r.get("name")),
                        "device_type": r.get("Device Type", r.get("type")),
                        "status": r.get("Status", r.get("status")),
                        "_source_sheet": sheet_name
                    })
            elif "port" in s_name:
                for r in rows:
                    dataset["ports"].append({
                        "fact_type": "PortFact",
                        "device_name": r.get("Device Name"),
                        "port_name": r.get("Port Name"),
                        "port_status": r.get("Port Status"),
                        "_source_sheet": sheet_name
                    })
            elif "link" in s_name:
                for r in rows:
                    dataset["links"].append({
                        "fact_type": "LinkFact",
                        "src_device": r.get("Source Device"),
                        "src_port": r.get("Source Port"),
                        "dst_device": r.get("Dest Device"),
                        "dst_port": r.get("Dest Port"),
                        "_source_sheet": sheet_name
                    })
        
        return dataset
