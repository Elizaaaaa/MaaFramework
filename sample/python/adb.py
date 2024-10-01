import time

from maa.resource import Resource
from maa.controller import AdbController
from maa.tasker import Tasker
from maa.toolkit import Toolkit
from maa.context import Context
from maa.define import MaaAdbScreencapMethodEnum

from maa.custom_recognition import CustomRecognition
from maa.custom_action import CustomAction

import wabaoAction as wabao


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

    resource.register_custom_action("PressZ", wabao.PressZ())
    resource.register_custom_action("WaitAct", wabao.WaitAct())
    resource.register_custom_recognition("RunKaishi", wabao.FindKaishi())
    resource.register_custom_recognition("RunFaxian", wabao.FindFaxian())
    resource.register_custom_recognition("RunBaopos", wabao.FindBaoPos())

    image = controller.cached_image
    wabao.save_to_file(image, user_path+"/savedImage.png")

    task_detail = tasker.post_pipeline("StartWabao").wait().get()
    #if task_detail:
        # print(f"pipeline detail: {task_detail}")
    if task_detail is None:
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


if __name__ == "__main__":
    main()
