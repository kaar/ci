from ci import main


def test_ci():
    diff = """
diff --git a/ci/main.py b/ci/main.py
index 149731e..1f616fb 100644
--- a/ci/main.py
+++ b/ci/main.py
@@ -1,11 +1,27 @@
+import logging
+import os
+
 import openai
 
 from . import git
 
+LOGGER = logging.getLogger(__name__)
 DEFAULT_MODEL = "gpt-3.5-turbo"
 
 
+def setup_logging():
+    DEBUG = os.environ.get("DEBUG", False)
+    log_level = logging.DEBUG if __debug__ or DEBUG else logging.INFO
+    logging.basicConfig(
+        level=log_level,
+        format="%(asctime)s %(levelname)s %(message)s",
+        datefmt="%Y-%m-%d %H:%M:%S",
+    )
+    LOGGER.debug("Debug mode enabled")
+
+
 def ci():
+    setup_logging()
     input_diff = git.cached_diff()
     # input_diff = sys.stdin.read()
 
    """
    commit_msg = main.generate_commit(input_diff=diff)

    print(commit_msg)
