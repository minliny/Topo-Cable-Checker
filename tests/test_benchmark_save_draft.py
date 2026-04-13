import time
from src.infrastructure.repository import BaselineRepository
from src.application.rule_editor_services.rule_draft_save_service import RuleDraftSaveService
from src.domain.baseline_model import BaselineProfile

def test_benchmark_save_draft_performance():
    import tempfile
    import os
    import shutil
    import src.infrastructure.repository as repo_module
    
    # Use a clean temporary directory for the benchmark
    tmp_dir = tempfile.mkdtemp()
    original_data_dir = repo_module.DATA_DIR
    original_backup_dir = repo_module.BACKUP_DIR
    repo_module.DATA_DIR = tmp_dir
    repo_module.BACKUP_DIR = os.path.join(tmp_dir, "backups")
    os.makedirs(repo_module.BACKUP_DIR, exist_ok=True)
    
    repo = BaselineRepository()
    svc = RuleDraftSaveService(repo)
    
    b = BaselineProfile(baseline_id="perf_baseline", baseline_version="1.0", recognition_profile={}, naming_profile={}, rule_set={})
    repo.save(b)
    
    start = time.time()
    for i in range(100):
        svc.save_draft("perf_baseline", {
            "rule_set": {
                f"rule_{i}": {
                    "template": "threshold",
                    "params": {"val": i}
                }
            },
            "active_rule_id": f"rule_{i}"
        })
    end = time.time()
    
    duration = end - start
    print(f"\n[Benchmark] 100 saves took {duration:.3f}s")
    
    # Restore original dirs
    repo_module.DATA_DIR = original_data_dir
    repo_module.BACKUP_DIR = original_backup_dir
    shutil.rmtree(tmp_dir)
    
    assert duration < 1.0, f"Performance issue: took {duration}s"
