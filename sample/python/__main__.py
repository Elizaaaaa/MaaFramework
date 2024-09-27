import time
# python -m pip install maafw
from maa.resource import Resource
from maa.controller import AdbController
from maa.tasker import Tasker
from maa.toolkit import Toolkit

from maa.custom_recognition import CustomRecognition
from maa.custom_action import CustomAction


def main():
    user_path = "./"
    Toolkit.init_option(user_path)

    resource = Resource()
    res_job = resource.post_path("sample/resource")
    res_job.wait()

    adb_devices = Toolkit.find_adb_devices()
    if not adb_devices:
        print("No ADB device found.")
        exit()

    # for demo, we just use the first device
    device = adb_devices[0]
    controller = AdbController(
        adb_path=device.adb_path,
        address=device.address,
        screencap_methods=device.screencap_methods,
        input_methods=device.input_methods,
        config=device.config,
    )
    controller.post_connection().wait()

    tasker = Tasker()
    tasker.bind(resource, controller)

    if not tasker.inited:
        print("Failed to init MAA.")
        exit()

    maa_inst.register_action("RepeatPickUpAll", pickUpAll)

    task_detail = tasker.post_pipeline("StartUpAndClickButton").wait().get()
    # do something with task_detail


class MyRecongition(CustomRecognition):

    def analyze(
        self,
        context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        reco_detail = context.run_recognition(
            "MyCustomOCR",
            argv.image,
            pipeline_override={"MyCustomOCR": {"roi": [100, 100, 200, 300]}},
        )

        # context is a reference, will override the pipeline for whole task
        context.override_pipeline({"MyCustomOCR": {"roi": [1, 1, 114, 514]}})
        # context.run_recognition ...

        # make a new context to override the pipeline, only for itself
        new_context = context.clone()
        new_context.override_pipeline({"MyCustomOCR": {"roi": [100, 200, 300, 400]}})
        reco_detail = new_context.run_recognition("MyCustomOCR", argv.image)

        click_job = context.tasker.controller.post_click(10, 20)
        click_job.wait()

class RepeatPickupAll(CustomAction):
    def run(self, context, task_name, custom_param, box, rec_detail) -> bool:
        print(
            f"on RepeatPickupAll.run, task_name: {task_name}, custom_param: {custom_param}, box: {box}, rec_detail: {rec_detail}"
        )
        for _ in range(5):
            context.press_key(90) #Press Z for 5 times
            time.sleep(0.2)

        return True

    def stop(self) -> None:
        pass

pickUpAll = RepeatPickupAll();


if __name__ == "__main__":
    main()
