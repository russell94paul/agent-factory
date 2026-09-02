# Pipeline Optimization and Object-Agnostic Experimental Engine

## Pipeline telemetry

Store pipeline/job/run information such as:

- pipeline
- run
- job
- task
- duration
- queue time
- compute
- warehouse
- rows
- bytes
- retries
- failure class
- cost
- SLA
- freshness
- data quality
- resource utilization
- config
- code version
- environment

## Pipeline Genome

Potential mutable fields:

- warehouse size
- parallelism
- batch size
- partition strategy
- retry policy
- task concurrency
- cache policy
- schedule
- resource requests
- query strategy
- materialization strategy

Possible objectives:

- cost down
- runtime down
- failures down
- SLA misses down
- freshness up
- throughput up

## Experimental Optimization Engine

Long term, avoid completely separate AgentOptimizer/TeamOptimizer/PipelineOptimizer implementations.

Create an object-agnostic engine that receives:

```text
SUBJECT
Agent / Team / Army / Pipeline / Retrieval System

CONFIGURATION SPACE
what may mutate

LOCKS
what may not mutate

OBJECTIVES
what should improve

CORPUS
how performance is tested

BUDGET
how much experimentation is allowed

CERTIFICATION
what proves success
```

Agent optimization and pipeline optimization become separate optimization schemas over the same experimental control plane.
