# Phony targets
.PHONY: all clean

clean:
	@find . -type d -name "__pycache__" -exec rm -r {} +
