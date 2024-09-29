import time
from PIL import Image
import numpy as np

from maa.resource import Resource
from maa.controller import Win32Controller
from maa.tasker import Tasker
from maa.toolkit import Toolkit
from maa.context import Context
from maa.define import MaaWin32ScreencapMethodEnum, MaaWin32InputMethodEnum

from maa.custom_recognition import CustomRecognition
from maa.custom_action import CustomAction

win32_screencap_type = MaaWin32ScreencapMethodEnum.FramePool
win32_input_type = MaaWin32InputMethodEnum.SendMessage


def main():
    user_path = "D:/Projects/MaaFramework/sample"
    Toolkit.init_option(user_path)

    resource = Resource()
    res_job = resource.post_path("D:/Projects/MaaFramework/sample/resource")
    res_job.wait()

    controller = getWin32Controller()
    if controller:
        if controller.post_connection().failed():
            print(f"Failed to connect device.")

    tasker = Tasker()
    tasker.bind(resource, controller)
    time.sleep(1)
    if not tasker.inited:
        print("Failed to init MAA.")
        exit(1)

    resource.register_custom_action("PressR", PressR())
    resource.register_custom_action("PressZ", PressZ())

    controller.set_screenshot_target_long_side(1080)
    controller.set_screenshot_target_short_side(720)
    controller.post_screencap().wait()
    image = controller.cached_image
    save_to_file(image, user_path+"/savedImage.png")

    ppover = {
        "Entry": {"next": "PressR"},
        "PressR": {
            "action": "Custom",
            "custom_action": "PressR",
            "custom_action_param": "RRRRRRRRRRRRRRRRR"
        },
        "PressZ": {
            "action": "Custom",
            "custom_action": "PressZ",
            "custom_action_param": "ZZZZZZZZZZZZZZZZZZZZ"
        }
    }

    task_detail = tasker.post_pipeline("Entry", ppover).wait().get()
    if task_detail:
        print(f"pipeline detail: {task_detail}")
    else:
        print("pipeline failed")
        raise RuntimeError("pipeline failed")
    
    #Toolkit.pi_run_cli("D:/Projects/MaaFramework/sample/resource", "D:/Projects/MaaFramework/sample/cache", False)

def getWin32Controller():
    window_list = Toolkit.find_desktop_windows()
    for window in window_list:
        # find J3 window
        if "KGWin32App" in window.class_name:
            return Win32Controller(window.hwnd,
                                   screencap_method=win32_screencap_type,
                                   input_method=win32_input_type)

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
            controller.post_press_key(90).wait()
            print("pressed R!")
            time.sleep(1)

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
            f"on PressR.run, context: {context}, task_detail: {argv.task_detail}, action_name: {argv.custom_action_name}, action_param: {argv.custom_action_param}, box: {argv.box}, reco_detail: {argv.reco_detail}"
        )

        controller = context.tasker.controller
        for _ in range(5):
            controller.post_press_key(82).wait()
            print("pressed R!")
            time.sleep(1)

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
