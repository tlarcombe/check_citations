SKILL_NAME := check-citations
SKILL_DIR := $(HOME)/.claude/skills/$(SKILL_NAME)
SRC_DIR := $(CURDIR)/skill

.PHONY: deploy undeploy test

deploy:
	mkdir -p $(SKILL_DIR)/references $(SKILL_DIR)/assets
	cp $(SRC_DIR)/SKILL.md $(SKILL_DIR)/SKILL.md
	cp $(SRC_DIR)/references/* $(SKILL_DIR)/references/ 2>/dev/null || true
	@echo "Deployed $(SKILL_NAME) to $(SKILL_DIR)"

undeploy:
	rm -rf $(SKILL_DIR)
	@echo "Removed $(SKILL_NAME)"

test:
	.venv/bin/pytest tests/ -v
