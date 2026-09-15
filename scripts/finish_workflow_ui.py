from pathlib import Path

web = Path('src/stockforge/web_app.py')
s = web.read_text(encoding='utf-8')
# Add a visible durable pipeline monitor.
s = s.replace('let referenceId=null, jobId=null, pollTimer=null;', 'let referenceId=null, workflowId=null, jobId=null, pollTimer=null, workflowTimer=null;', 1)
s = s.replace('<section class="card"><h2>2. Define a new creative opportunity</h2>', '<section class="card"><h2>Pipeline monitor</h2><p id="workflowStatus" class="status">No workflow yet.</p><div id="workflowProgress"></div><pre id="workflowResult">Upload a reference to start durable tracking.</pre></section><section class="card"><h2>2. Define a new creative opportunity</h2>', 1)
s = s.replace("referenceId=result.reference_id;show('profile',result.profile);$('plan').disabled=false;show('referenceStatus','Reference ready: '+referenceId)", "referenceId=result.reference_id;workflowId=result.workflow_id;show('profile',result.profile);$('plan').disabled=false;show('referenceStatus','Reference ready: '+referenceId);startWorkflowPolling()", 1)
s = s.replace("jobId=result.job_id;show('jobStatus','Queued: '+jobId);pollTimer=setInterval(pollJob,1500);await pollJob()", "workflowId=result.workflow_id||workflowId;jobId=result.job_id;show('jobStatus','Queued: '+jobId);startWorkflowPolling();pollTimer=setInterval(pollJob,1500);await pollJob()", 1)
s = s.replace('function renderArtifacts(result){', "function startWorkflowPolling(){if(!workflowId)return;if(workflowTimer)clearInterval(workflowTimer);workflowTimer=setInterval(pollWorkflow,1500);pollWorkflow()}\nasync function pollWorkflow(){if(!workflowId)return;try{const wf=await api('/api/workflows/'+workflowId);const pct=wf.progress||0;show('workflowStatus',wf.current_stage+' — '+pct+'% — '+wf.status+(wf.stuck?' — MAY BE STUCK':''));$('workflowProgress').innerHTML='<progress max=\"100\" value=\"'+pct+'\" style=\"width:100%;height:18px\"></progress><p><small>Last update: '+(wf.updated_at||'n/a')+'</small></p>';show('workflowResult',wf);if(['ready','blocked','failed','cancelled'].includes(wf.status)){clearInterval(workflowTimer);workflowTimer=null}}catch(e){show('workflowStatus','Monitor error: '+e.message)}}\nfunction renderArtifacts(result){", 1)
web.write_text(s, encoding='utf-8')

# Regeneration must reopen the same workflow and point it at the child job.
s = web.read_text(encoding='utf-8')
old = '    child = manager.create(project_id=PROJECT_ID, job_type="v2_generation", payload=payload, max_attempts=2)\n    return {"reference_id": parameters.get("reference_id"), "job_id": child.id, "parent_job_id": job_id, "regeneration_attempt": attempt + 1, "max_regeneration_attempts": maximum, "status": child.status, "decision": "REGENERATION_QUEUED"}\n'
new = '    child = manager.create(project_id=PROJECT_ID, job_type="v2_generation", payload=payload, max_attempts=2)\n    control = WorkflowControl(manager.database)\n    control.initialize()\n    workflow = control.get_for_reference(str(parameters.get("reference_id"))) if parameters.get("reference_id") else None\n    if workflow:\n        control.attach_job(workflow["id"], child.id)\n        control.event(workflow["id"], stage="QUEUED", status="active", message="Regeneration queued after similarity block.", job_id=child.id, details={"parent_job_id": job_id, "regeneration_attempt": attempt + 1})\n    return {"reference_id": parameters.get("reference_id"), "workflow_id": workflow["id"] if workflow else None, "job_id": child.id, "parent_job_id": job_id, "regeneration_attempt": attempt + 1, "max_regeneration_attempts": maximum, "status": child.status, "decision": "REGENERATION_QUEUED"}\n'
if old not in s: raise SystemExit('regeneration block not found')
s = s.replace(old, new, 1)
web.write_text(s, encoding='utf-8')
