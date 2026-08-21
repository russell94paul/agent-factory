# Agent Factory / Zeus Pantheon Suite — original brain dump

Recovered verbatim from session `d5248a7f` after the 2026-08-20 20:16 VS Code crash.
Two versions: the 20:04 one is the final, expanded brief that produced
`agent-factory-research-prompts.md`. The 18:47 one is kept because it is not a strict subset.

---

## Final version — 2026-08-20 20:04 (5929 chars)

Can you convert this into a research promp

I think we need to create a new repo with zip file to spin the whole skeelton up maybe for this Agent Factory - skeleton spun up from architecture diagrams and artifacts

Zeus Panthenon Suite brain dump

Here are list of artifacts we need to review and synthesize when putting together the full thing.
https://claude.ai/code/artifact/931d5e8e-d2a0-4d5b-a185-880a325b182d?via=auto_preview
https://claude.ai/code/artifact/a78ef1dd-12dc-4a8b-bd53-3ac254b27ceb?via=auto_preview
https://claude.ai/code/artifact/931d5e8e-d2a0-4d5b-a185-880a325b182d
https://claude.ai/code/artifact/6c32a475-59a9-42e0-ac65-4e818079cce9?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/931d5e8e-d2a0-4d5b-a185-880a325b182d?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/a78ef1dd-12dc-4a8b-bd53-3ac254b27ceb?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/931d5e8e-d2a0-4d5b-a185-880a325b182d?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/d1641059-96ce-480c-87c7-e795ce653b28?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/b238c86e-edb5-4c49-bc77-c8c56fce3131?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/d1641059-96ce-480c-87c7-e795ce653b28?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/6c32a475-59a9-42e0-ac65-4e818079cce9?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/00596dc2-c17a-428a-8a07-3c9650c52745?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8

Other ideas:
please recommend sections and layouts we should include - especially the technical doc information
We should clearly define what Agent Army, Agent Team Agents consist off how the can be configured, communicate with eachother
maybe there should be an agent or agent team responsible for picking the correct team members for a specific task

the agent army  agent team or agent should iterate on the task until the optimal configuration is found - then deploy the team on the real run.

should each army, team, agent store run data to allow agent versioning

Types of Teams: most teams highly configurable
Zeus Chat
Snowflake
Zeus Foundry
Monitoring/Alerting - token overage alert then optimize using autoresearcher or another tool
API Team
Model Selection
Optimization Team
Triage Team
Defect Resolution Team
Client Team (GEP, Fusion92)
R&D

Other features:
Interactive UI - Globally 
Multi-Tab - not sure what tabs yet on tab dedicated to breaking down the implementation and integration details etc maybe a zip file to boot the whole repo and a guide on which md files etc to use and run etc
Agentic Gym to train Agent Army, Agent Team Manager, Agent Team  and Agents
maybe a generic autoresearcher component that can be configured to optimize anything in the system is degrading

Agent Communication Module:
Agent to Agent
Agent Team Manager to Agent
Agent Team Manager to Agent Team Manager
Agent Army to one or many Agent Team Managers
Agent Army to Agent Army

Review and optimize my thoughts above and research the optimal approach for our company
autoresearcher tool for optimization - unsure what level the optimization tool should be at (I think it should be configurable depending on the 

Interactive Agent Factory Dashboard with all key metrics for different army/teams/agents
 
This is all I can think of

There should be a simulator tool for constructing the optimal agent army/agent manager/agent for the task/project (

Technical Diagrams:
System overview
apps
snowflake
infrastructure
Data flow
Use-cases - find simpler ones from prospect sites (include food bank canada)

optinal - Analytic Brand video walkthrough highlighting the technical improvments/benefits from the system

identify all repos/infrastructure/access/credentials  required and the proces of deploying an agent army, agent team manager, agent team , agent

please recommend a detailed research prompts to run to ensure we implement this in the most optimal robust adaptable way

Priority - Build the Agentic Data Pipeline Team (Connnector Migration , Connector onboarding future)
Priority - ensure we are tracking all metrics to improve component by component and and the over all pipeline

please include a zip file that can help me spin up this repo in a robust scalable design

please review these ideas , optimize them add or remove components i etc.

Extremely important to include:
Platform UI
AgnosticOptimizer (autoresearch https://github.com/karpathy/autoresearch) - may need some modifications - interactive visualization
Maybe a UI might help to put on early on
For every optimizer run a sandbox will need to spun up for safety when doing the iteration

Data Pipeline Team - need to build/migrate connectors, land in snowflake then Power BI for now  e2e - green (not sure if we should just include snowflake. power bi on this team) - need to get GP-318 fully finished e2e today at least

I guesss the Agnostic optimizer can cover all that.

Research Module:
Also do a review of the whole system and determine if we need to do some chatgpt research prompts before design and implementing (maybe you can do this autonomously with claude-in-chrome and drop into research folder.
Whenever a new piece of research comes in, it gets synthesized into Busines and Tech Spec and gets passed to the R&D team to run the optimizer until 


I want this interactive configurable artifact to cover the entire system:
if possible allow them to be drill down into each component from top-level diagram to lower level with arrows showing what operation was done the data that is moving forward

once we create the research prompt we should create an overall artifact using claude that contains everything we need to build out this system efficiently

if there is a tool that can spin up most of the repo that might be worth researching.

Dig Deep on this one

---

## Earlier version — 2026-08-20 18:47 (3719 chars)

I think we need to create a new repo maybe for this Agent Factory

Zeus Panthenon Suite

Here are list of artifacts we need to review and synthesize when putting together the full thing.
https://claude.ai/code/artifact/931d5e8e-d2a0-4d5b-a185-880a325b182d?via=auto_preview
https://claude.ai/code/artifact/a78ef1dd-12dc-4a8b-bd53-3ac254b27ceb?via=auto_preview
https://claude.ai/code/artifact/931d5e8e-d2a0-4d5b-a185-880a325b182d
https://claude.ai/code/artifact/6c32a475-59a9-42e0-ac65-4e818079cce9?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/931d5e8e-d2a0-4d5b-a185-880a325b182d?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/a78ef1dd-12dc-4a8b-bd53-3ac254b27ceb?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/931d5e8e-d2a0-4d5b-a185-880a325b182d?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/d1641059-96ce-480c-87c7-e795ce653b28?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/b238c86e-edb5-4c49-bc77-c8c56fce3131?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/d1641059-96ce-480c-87c7-e795ce653b28?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/6c32a475-59a9-42e0-ac65-4e818079cce9?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8
https://claude.ai/code/artifact/00596dc2-c17a-428a-8a07-3c9650c52745?org=0ce21ee0-ec76-4ae4-8551-abbfbee061f8

Other ideas:
please recommend sections and layouts we should include - especially the technical doc information
We should clearly define what Agent Army, Agent Team Agents consist off how the can be configured, communicate with eachother
maybe there should be an agent or agent team responsible for picking the correct team members for a specific task

the agent army  agent team or agent should iterate on the task until the optimal configuration is found - then deploy the team on the real run.

should each army, team, agent store run data to allow agent versioning

Types of Teams:
Zeus Chat
Snowflake
Zeus Foundry
Monitoring/Alerting
API
Model Selection
Optimization Team
Triage Team
Defect Resolution Team
Client Team (GEP, Fusion92

Other features:
Interactive UI
Multi-Tab - not sure what tabs yet on tab dedicated to breaking down the implementation and integration details etc maybe a zip file to boot the whole repo and a guide on which md files etc to use and run etc

Review and optimize my thoughts above and research the optimal approach for our company
autoresearcher tool for optimization - unsure what level the optimization tool should be at (I think it should be configurable depending on the 

Interactive Agent Factory Dashboard with all key metrics for different army/teams/agents

This is all I can think of

There should be a simulator tool for constructing the optimal agent army/agent manager/agent for the task/project

Technical Diagrams:
System overview
apps
snowflake
infrastructure
Data flow
Use-cases - find simpler ones from prospect sites (include food bank canada)

optinal - Analytic Brand video walkthrough highlighting the technical improvments/benefits from the system

identify all repos/infrastructure/access/credentials  required and the proces of deploying an agent army, agent team manager, agent team , agent

please recommend a detailed research prompts to run to ensure we implement this in the most optimal robust adaptable way

Priority - Build the Agentic Data Pipeline Team
Priority - ensure we are tracking all metrics to improve component by component and and the over all pipeline

please include a zip file that can help me spin up this repo in a robust scalable design

please review these ideas , optimize them add or remove components i etc.
