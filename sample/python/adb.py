import time
from PIL import Image
import numpy as np
import json

from maa.resource import Resource
from maa.controller import AdbController
from maa.tasker import Tasker
from maa.toolkit import Toolkit
from maa.context import Context
from maa.define import MaaAdbScreencapMethodEnum

from maa.custom_recognition import CustomRecognition
from maa.custom_action import CustomAction


adb_screencap_type = MaaAdbScreencapMethodEnum.Encode


def main():
    user_path = "D:/Projects/MaaFramework/sample"
    Toolkit.init_option(user_path)

    resource = Resource()
    res_job = resource.post_path("D:/Projects/MaaFramework/sample/resource")
    res_job.wait()

    controller = getAdbController()
    if controller:
        if controller.post_connection().failed():
            print(f"Failed to connect device.")
            exit(1)

    controller.set_screenshot_target_long_side(1920)
    controller.set_screenshot_target_short_side(1080)
    controller.post_screencap().wait()

    tasker = Tasker()
    tasker.bind(resource, controller)
    time.sleep(1)
    if not tasker.inited:
        print("Failed to init MAA.")
        exit(1)

    resource.register_custom_action("PressR", PressR())
    resource.register_custom_action("PressZ", PressZ())
    resource.register_custom_action("WaitAct", WaitAct())

    image = controller.cached_image
    save_to_file(image, user_path+"/savedImage.png")

    task_detail = tasker.post_pipeline("StartWabao").wait().get()
    if task_detail:
        print(f"pipeline detail: {task_detail}")
    else:
        print("pipeline failed")
        raise RuntimeError("pipeline failed")
        
def getAdbController():
    device_list = Toolkit.find_adb_devices()
    for device in device_list:
        # jx3 adb port: 16384
        if "16384" in device.address:
            return AdbController(adb_path=device.adb_path,
                                 address=device.address,
                                 screencap_methods=device.screencap_methods,
                                 input_methods=device.input_methods,
                                 config=device.config)

class PressZ(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        print(
            f"on PressZ.run, context: {context}, task_detail: {argv.task_detail}, action_name: {argv.custom_action_name}, action_param: {argv.custom_action_param}, box: {argv.box}, reco_detail: {argv.reco_detail}"
        )

        controller = context.tasker.controller
        for _ in range(5):
            controller.post_press_key(0x00000036).wait()
            print("pressed Z!")
            time.sleep(0.2)

        global runned
        runned = True

        return CustomAction.RunResult(success=True)

class PressR(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        print(
            f"on PressR.run, context: {context}, task_detail: {argv.task_detail}, action_name: {argv.custom_action_name}"
        )

        controller = context.tasker.controller
        job = controller.post_press_key(0x0000002e).wait()

        global runned
        runned = True
        
        return CustomAction.RunResult(success=job.succeeded())
    
class PressT(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        print(
            f"on PressT.run, context: {context}, task_detail: {argv.task_detail}, action_name: {argv.custom_action_name}"
        )

        controller = context.tasker.controller
        job = controller.post_press_key(0x00000030).wait()

        global runned
        runned = True
        
        return CustomAction.RunResult(success=job.succeeded())
    
class WaitAct(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        print(
            f"on PressR.run, context: {context}, task_detail: {argv.task_detail}, action_name: {argv.custom_action_name}, action_param: {argv.custom_action_param}"
        )

        action_params = json.loads(argv.custom_action_param)
        sleepTime = float(action_params["wait_time"])
        time.sleep(sleepTime)

        global runned
        runned = True
        
        return CustomAction.RunResult(success=True)


def save_to_file(image_array: np.ndarray, filename: str):
    if image_array.shape[-1] == 3:
        image_array = image_array[..., ::-1]
    # Convert the NumPy array to a Pillow image
    image = Image.fromarray(image_array)
    
    # Save the image to the specified file
    image.save(filename)
    print(f"Image saved to {filename}")


if __name__ == "__main__":
    main()
