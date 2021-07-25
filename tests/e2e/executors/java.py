import subprocess
from os import environ
from pathlib import Path
from shutil import copyfile

from m2cgen import export_to_java

from tests import utils
from tests.e2e.executors.base import BaseExecutor


class JavaExecutor(BaseExecutor):

    def __init__(self, model):
        self.model = model
        self.class_name = "Model"

        java_home = environ.get("JAVA_HOME")
        assert java_home, "JAVA_HOME is not specified"
        java_home = Path(java_home)
        self._java_bin = java_home / "bin" / "java"
        self._javac_bin = java_home / "bin" / "javac"

    def predict(self, X):
        exec_args = [
            str(self._java_bin),
            "-cp",
            str(self._resource_tmp_dir),
            "Executor",
            "Model",
            "score",
            *map(utils.format_arg, X)
        ]
        return utils.predict_from_commandline(exec_args)

    def prepare(self):
        # Create files generated by exporter in the temp dir.
        code = export_to_java(self.model, class_name=self.class_name)
        code_file_name = self._resource_tmp_dir / f"{self.class_name}.java"
        utils.write_content_to_file(code, code_file_name)

        # Move Executor.java to the same temp dir.
        module_path = Path(__file__).absolute().parent
        executor_path = self._resource_tmp_dir / "Executor.java"
        copyfile(module_path / "Executor.java", executor_path)

        # Compile all files together.
        subprocess.call([
            str(self._javac_bin),
            str(code_file_name),
            str(executor_path)
        ])
