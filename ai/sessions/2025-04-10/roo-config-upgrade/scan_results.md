# Repository Structure Scan Results (cli & ai)

**Date:** 2025-04-10

**Objective:** Analyze the directory structures of `cli/` and `ai/` relevant to agent definitions and the `cli` tool, excluding cache directories.

---

## 1. `cli/` Directory Structure:

```json
[
  {
    "name": "agent_config",
    "type": "directory",
    "children": [
      {
        "name": "__init__.py",
        "type": "file"
      },
      {
        "name": "commands.py",
        "type": "file"
      },
      {
        "name": "markdown_utils.py",
        "type": "file"
      },
      {
        "name": "models.py",
        "type": "file"
      },
      {
        "name": "settings.py",
        "type": "file"
      }
    ]
  },
  {
    "name": "config.yaml",
    "type": "file"
  },
  {
    "name": "constants.py",
    "type": "file"
  },
  {
    "name": "main.py",
    "type": "file"
  }
]
```

---

## 2. `ai/` Directory Structure (Agent Definitions &amp; Related):

```json
[
  {
    "name": ".franchises",
    "type": "directory",
    "children": [
      {
        "name": "rawr",
        "type": "directory",
        "children": [
          {
            "name": "captains",
            "type": "directory",
            "children": [
              {
                "name": "captain_defense.md",
                "type": "file"
              },
              {
                "name": "captain_offense.md",
                "type": "file"
              },
              {
                "name": "captain_special.md",
                "type": "file"
              }
            ]
          },
          {
            "name": "coaches",
            "type": "directory",
            "children": [
              {
                "name": "coach_head-coach.md",
                "type": "file"
              },
              {
                "name": "coach_head-trainer.md",
                "type": "file"
              }
            ]
          },
          {
            "name": "players",
            "type": "directory",
            "children": [
              {
                "name": ".concepts",
                "type": "directory",
                "children": [
                  {
                    "name": "agent_defensive-coordinator.md",
                    "type": "file"
                  },
                  {
                    "name": "agent_general-manager.md",
                    "type": "file"
                  },
                  {
                    "name": "agent_head-coach.md",
                    "type": "file"
                  },
                  {
                    "name": "agent_head-trainer.md",
                    "type": "file"
                  },
                  {
                    "name": "agent_offensive-coordinator.md",
                    "type": "file"
                  },
                  {
                    "name": "agent_special-teams-coordinator.md",
                    "type": "file"
                  },
                  {
                    "name": "agents.md",
                    "type": "file"
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  },
  {
    "name": "_feedback",
    "type": "directory",
    "children": [
      {
        "name": "feedback_agent_code.md",
        "type": "file"
      },
      {
        "name": "feedback_agent_diagram.md",
        "type": "file"
      },
      {
        "name": "feedback_git.md",
        "type": "file"
      },
      {
        "name": "feedback_orchestrator.md",
        "type": "file"
      },
      {
        "name": "feedback_test.md",
        "type": "file"
      }
    ]
  },
  {
    "name": "agents",
    "type": "directory",
    "children": [
      {
        "name": "command",
        "type": "directory",
        "children": [
          {
            "name": ".archive",
            "type": "directory",
            "children": [
              {
                "name": "agent_orchestrate_01.md",
                "type": "file"
              },
              {
                "name": "agent_orchestrate_02.md",
                "type": "file"
              },
              {
                "name": "agent_orchestrate_03.md",
                "type": "file"
              }
            ]
          },
          {
            "name": "coordinator_pb",
            "type": "directory",
            "children": [
              {
                "name": "coordinator_pb.md",
                "type": "file"
              }
            ]
          },
          {
            "name": "orchestrator_generic.md",
            "type": "file"
          }
        ]
      },
      {
        "name": "defense",
        "type": "directory",
        "children": [
          {
            "name": ".archive",
            "type": "directory",
            "children": [
              {
                "name": "agent_debug_01.md",
                "type": "file"
              },
              {
                "name": "agent_review_01.md",
                "type": "file"
              },
              {
                "name": "agent_review_02.md",
                "type": "file"
              }
            ]
          },
          {
            "name": "agent_debug.md",
            "type": "file"
          },
          {
            "name": "agent_review.md",
            "type": "file"
          },
          {
            "name": "agent_test.md",
            "type": "file"
          }
        ]
      },
      {
        "name": "offense",
        "type": "directory",
        "children": [
          {
            "name": "agent_implement.md",
            "type": "file"
          },
          {
            "name": "refactor",
            "type": "directory",
            "children": [
              {
                "name": "agent_refactor.md",
                "type": "file"
              }
            ]
          }
        ]
      },
      {
        "name": "special",
        "type": "directory",
        "children": [
          {
            "name": ".archive",
            "type": "directory",
            "children": [
              {
                "name": "agent_arch-install_01.md",
                "type": "file"
              },
              {
                "name": "agent_kg-engineer_01.md",
                "type": "file"
              }
            ]
          },
          {
            "name": "agent_arch-install.md",
            "type": "file"
          },
          {
            "name": "agent_architect.md",
            "type": "file"
          },
          {
            "name": "agent_git.md",
            "type": "file"
          },
          {
            "name": "agent_kg-engineer.md",
            "type": "file"
          },
          {
            "name": "orchestrator_install.md",
            "type": "file"
          }
        ]
      },
      {
        "name": "support",
        "type": "directory",
        "children": [
          {
            "name": "agent_document.md",
            "type": "file"
          }
        ]
      },
      {
        "name": "testing",
        "type": "directory",
        "children": [
          {
            "name": "temp_test_agent.md",
            "type": "file"
          }
        ]
      },
      {
        "name": "training",
        "type": "directory",
        "children": [
          {
            "name": ".archive",
            "type": "directory",
            "children": [
              {
                "name": "agent_prompt_01.md",
                "type": "file"
              },
              {
                "name": "agent_prompt_02.md",
                "type": "file"
              },
              {
                "name": "agent_prompt_03.md",
                "type": "file"
              }
            ]
          },
          {
            "name": "agent_position_coach.md",
            "type": "file"
          },
          {
            "name": "agent_prompt.md",
            "type": "file"
          }
        ]
      },
      {
        "name": "util",
        "type": "directory",
        "children": [
          {
            "name": "agent_ask.md",
            "type": "file"
          },
          {
            "name": "agent_diagram.md",
            "type": "file"
          },
          {
            "name": "agent_plan.md",
            "type": "file"
          },
          {
            "name": "agent_scan.md",
            "type": "file"
          },
          {
            "name": "agent_search.md",
            "type": "file"
          }
        ]
      }
    ]
  },
  {
    "name": "context",
    "type": "directory",
    "children": [
      {
        "name": "agent_config_conventions.md",
        "type": "file"
      },
      {
        "name": "agent_mandates.md",
        "type": "file"
      },
      {
        "name": "agent_orchestration_system.md",
        "type": "file"
      },
      {
        "name": "agent_org_chart.md",
        "type": "file"
      },
      {
        "name": "agent_system_architecture.md",
        "type": "file"
      },
      {
        "name": "franchise_roster.md",
        "type": "file"
      },
      {
        "name": "graphiti-core-principles.md",
        "type": "file"
      },
      {
        "name": "official_roo-custom-modes.md",
        "type": "file"
      },
      {
        "name": "orchestrator_SOPs.md",
        "type": "file"
      }
    ]
  },
  {
    "name": "graph",
    "type": "directory",
    "children": [
      {
        "name": "entities",
        "type": "directory",
        "children": [
          {
            "name": ".gitkeep",
            "type": "file"
          },
          {
            "name": "Entry.py",
            "type": "file"
          }
        ]
      },
      {
        "name": "mcp-config.yaml",
        "type": "file"
      },
      {
        "name": "plays",
        "type": "directory",
        "children": [
          {
            "name": "custom_modes.json",
            "type": "file"
          }
        ]
      }
    ]
  },
  {
    "name": "journal",
    "type": "directory",
    "children": [
      {
        "name": "2025-04-06_configure-diagram-agent.md",
        "type": "file"
      },
      {
        "name": "2025-04-06_create-agent-config-script.md",
        "type": "file"
      },
      {
        "name": "2025-04-06_create-diagram-agent.md",
        "type": "file"
      },
      {
        "name": "2025-04-06_create-entry-kg-entity.md",
        "type": "file"
      },
      {
        "name": "2025-04-06_create-position-coach-agent-and-refine-workflow.md",
        "type": "file"
      },
      {
        "name": "2025-04-06_update-orchestrator-sops-prompt.md",
        "type": "file"
      },
      {
        "name": "2025-04-06_update-roo-agent-mode-config.md",
        "type": "file"
      },
      {
        "name": "2025-04-07_agent-prompt-updates.md",
        "type": "file"
      },
      {
        "name": "2025-04-08_pytest-setup.md",
        "type": "file"
      },
      {
        "name": "2025-04-08_refactor-agent-config-manager.md",
        "type": "file"
      },
      {
        "name": "2025-04-09_cli-preserve-groups.md",
        "type": "file"
      },
      {
        "name": "2025-04-09_cli_refactoring.md",
        "type": "file"
      },
      {
        "name": "2025-04-10_cli-ux-improvements.md",
        "type": "file"
      }
    ]
  },
  {
    "name": "playbooks",
    "type": "directory",
    "children": [
      {
        "name": "pb_create_new_agent.md",
        "type": "file"
      },
      {
        "name": "pb_create_playbook.md",
        "type": "file"
      },
      {
        "name": "pb_discovery_driven_execution.md",
        "type": "file"
      },
      {
        "name": "pb_iterative_execution_verification.md",
        "type": "file"
      },
      {
        "name": "pb_refactor_codebase.md",
        "type": "file"
      },
      {
        "name": "pb_registry.md",
        "type": "file"
      },
      {
        "name": "pb_session_journaling.md",
        "type": "file"
      }
    ]
  },
  {
    "name": "projects",
    "type": "directory",
    "children": [
      {
        "name": "cli-yaml-config",
        "type": "directory",
        "children": [
          {
            "name": "yaml_config_ideas.md",
            "type": "file"
          }
        ]
      },
      {
        "name": "project_drafts.md",
        "type": "file"
      }
    ]
  },
  {
    "name": "sessions",
    "type": "directory",
    "children": [
      {
        "name": "2025-04-06",
        "type": "directory",
        "children": [
          {
            "name": "agent-config-script",
            "type": "directory",
            "children": [
              {
                "name": "agent-config-script.md",
                "type": "file"
              }
            ]
          },
          {
            "name": "cli-test-suite-setup",
            "type": "directory",
            "children": [
              {
                "name": "test_results.log",
                "type": "file"
              }
            ]
          },
          {
            "name": "configure-diagram-agent-and-update-orchestrator",
            "type": "directory",
            "children": [
              {
                "name": "full_workflow_diagram.md",
                "type": "file"
              },
              {
                "name": "full_workflow_diagram.mmd",
                "type": "file"
              }
            ]
          },
          {
            "name": "refactor-cli",
            "type": "directory",
            "children": [
              {
                "name": "cli_refactor_spec.md",
                "type": "file"
              },
              {
                "name": "custom_modes.json",
                "type": "file"
              },
              {
                "name": "rawr_cli_conceptual_tests.md",
                "type": "file"
              },
              {
                "name": "refactored_cli_workflow.mmd",
                "type": "file"
              }
            ]
          }
        ]
      },
      {
        "name": "2025-04-07",
        "type": "directory",
        "children": [
          {
            "name": "add-scan-agent",
            "type": "directory",
            "children": [
              {
                "name": "custom_modes.json",
                "type": "file"
              }
            ]
          },
          {
            "name": "agent-prompt-updates",
            "type": "directory",
            "children": [
              {
                "name": "workflow_diagram.mmd",
                "type": "file"
              },
              {
                "name": "workflow_plan.md",
                "type": "file"
              }
            ]
          }
        ]
      },
      {
        "name": "2025-04-08",
        "type": "directory",
        "children": [
          {
            "name": "old-test-suite-merge",
            "type": "directory",
            "children": [
              {
                "name": "manage_agent_configs.py",
                "type": "file"
              },
              {
                "name": "script_comparison.md",
                "type": "file"
              }
            ]
          },
          {
            "name": "pytest-setup",
            "type": "directory",
            "children": [
              {
                "name": "setup-test-suite-v2.md",
                "type": "file"
              }
            ]
          }
        ]
      },
      {
        "name": "2025-04-09",
        "type": "directory",
        "children": [
          {
            "name": "cli-preserve-groups.md",
            "type": "directory",
            "children": [
              {
                "name": "findings_report.md",
                "type": "file"
              },
              {
                "name": "implementation_plan.md",
                "type": "file"
              }
            ]
          },
          {
            "name": "cli-ux-improvements",
            "type": "directory",
            "children": [
              {
                "name": "analysis_report_step2b.md",
                "type": "file"
              },
              {
                "name": "magic_strings_log.md",
                "type": "file"
              },
              {
                "name": "plan_review_step5.md",
                "type": "file"
              },
              {
                "name": "rawr_implementation_recommendation.md",
                "type": "file"
              },
              {
                "name": "refactor_cli_ux_plan.md",
                "type": "file"
              }
            ]
          },
          {
            "name": "cli_refactor",
            "type": "directory",
            "children": [
              {
                "name": "analysis.md",
                "type": "file"
              },
              {
                "name": "refactor_plan.md",
                "type": "file"
              }
            ]
          },
          {
            "name": "create_agent_playbook",
            "type": "directory",
            "children": [
              {
                "name": "agent_creation_process.mermaid",
                "type": "file"
              },
              {
                "name": "analysis_summary.md",
                "type": "file"
              },
              {
                "name": "meta_playbook_analysis.md",
                "type": "file"
              },
              {
                "name": "pb_create_new_agent.md",
                "type": "file"
              },
              {
                "name": "pb_create_new_agent_draft.md",
                "type": "file"
              },
              {
                "name": "review_feedback.md",
                "type": "file"
              },
              {
                "name": "review_feedback_round2.md",
                "type": "file"
              }
            ]
          },
          {
            "name": "refactor-cli-yaml",
            "type": "directory",
            "children": [
              {
                "name": "pb_refactor_codebase_draft.md",
                "type": "file"
              },
              {
                "name": "pb_refactor_codebase_refined_draft.md",
                "type": "file"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    "name": "todo.md",
    "type": "file"
  }
]