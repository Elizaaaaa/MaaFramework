from maa.custom_recognition import CustomRecognition
from maa.custom_action import CustomAction
from maa.toolkit import Toolkit
from maa.context import Context

import time
from PIL import Image
import numpy as np
import json
from win10toast import ToastNotifier

class FindKaishi(CustomRecognition):
    def analyze(self, context: Context, argv: CustomRecognition.AnalyzeArg) -> CustomRecognition.AnalyzeResult:
        print(
            f"on FindKaishi.analyze"
        )
        controller = context.tasker.controller

        # 挖宝- 开始
        entry = "FindKaishiPos"
        ppover = {
            "FindKaishiPos": {
                "recognition": "OCR",
                "expected": "开始",
                "roi": [230, 240, 190, 190]
            },
            "BacktoGeren":{
                "recognition": "OCR",
                "expected": "返回个人寻宝",
                "roi": [0, 0, 1024, 1024]
            }
        }
        findKaishiResult = context.run_recognition(entry, argv.image, ppover)
        if findKaishiResult:
            print("点击开始寻宝")
            box = findKaishiResult.box
            controller.post_click(int(box.x+box.w/2), int(box.y+box.h/2)).wait()
        else:
            # 找不到是因为团点出现？
            fanhuiResult = context.run_recognition("BacktoGeren", argv.image, ppover)
            if fanhuiResult:
                print("发现团点！")
                # post 团点 notification
                toaster = ToastNotifier()
                toaster.show_toast("发现团点！", "快去找团点！", duration=10, threaded=True)
                print("点击返回个人藏宝")
                time.sleep(0.5)
                box = fanhuiResult.box
                controller.post_click(int(box.x+box.w/2), int(box.y+box.h/2)).wait()
                time.sleep(0.5)
                findKaishiResult = context.run_recognition(entry, argv.image, ppover)
                if findKaishiResult:
                    print("点击开始寻宝")
                    box = findKaishiResult.box
                    controller.post_click(int(box.x+box.w/2), int(box.y+box.h/2)).wait()
                else:
                    print("没有找到发现按钮！")

        time.sleep(0.5)

        global analyzed
        analyzed = True

        return CustomRecognition.AnalyzeResult(box=(0, 0, 100, 100), detail="")
    
class FindBaoPos(CustomRecognition):
    def analyze(self, context: Context, argv: CustomRecognition.AnalyzeArg) -> CustomRecognition.AnalyzeResult:
        print(
            f"on FindBaoPos.analyze"
        )
        controller = context.tasker.controller
        ppover = {
            "FindBaoPosAct": {
                "recognition": "FeatureMatch",
                "template": "baopos.png",
                "green_mask": True,
                "roi": [1220, 800, 300, 300]
            },
            "ColorMatch": {
                "recognition": "ColorMatch",
                "lower": [120, 200, 230],
                "upper": [130, 220, 255],
                "roi": [1220, 820, 150, 150],
                "action": "Click"
            },
            "FindCangbaodian":
            {
                "recognition": "OCR",
                "expected": "藏宝点"
            }
        }
        box = (1300, 880, 10, 10)
        result = None
        for _ in range(5):
            #尝试五遍
            time.sleep(0.2)
            controller.post_screencap().wait()
            image = controller.cached_image
            result = context.run_recognition("FindBaoPosAct", image, ppover)
            if result:
                if result.box.w < 100 and result.box.h < 100:
                    break
                else:
                    result = None # unqualified
        
        if result:
            print(result)
            box = result.box
            print(f"FindBaoPos - click {box}")
            controller.post_click(int(box.x+5), int(box.y+5)).wait()
            context.override_next(argv.current_task_name, ["FindZidongxunlu"])
        else:
            print(f"没找到藏宝点，尝试点击常出错的位置")
            controller.post_click(1310, 890).wait()
            time.sleep(1)
            controller.post_screencap().wait()
            image = controller.cached_image
            cangbaoResult = context.run_recognition("FindCangbaodian", image, ppover)
            if cangbaoResult:
                print(f"成功点击到藏宝点")
                context.override_next(argv.current_task_name, ["FindZidongxunlu"])
            else:
                print("没有找到藏宝点")
        global analyzed
        analyzed = True

        return CustomRecognition.AnalyzeResult(box=box, detail="")


class FindFaxian(CustomRecognition):
    def analyze(self, context: Context, argv: CustomRecognition.AnalyzeArg) -> CustomRecognition.AnalyzeResult:
        print(
            f"on FindFaxian.analyze"
        )
        controller = context.tasker.controller

        # 查找发现的位置
        entry = "FindFaxianPos"
        ppover = {
            "FindFaxianPos": {
                "recognition": "OCR",
                "expected": "发现",
                "roi": [1000, 200, 600, 400]
            }
        }
        image = argv.image
        result = context.run_recognition(entry, image, ppover)
        waitTime = 0
        while result is None:
            # wait until reach the pos
            print(f"Find 发现 for {waitTime} times")
            time.sleep(1)
            controller.post_screencap().wait()
            image = controller.cached_image
            result = context.run_recognition(entry, image, ppover)
            waitTime += 1
            if (waitTime > 60):
                # timeout after 60s
                print("Failed to find the Faxian Pos!")
                break
        
        if result:
            print(f"Found faxian:{result.box}")
            # 检查挖宝工具是否就绪
            entry = "WabaoRemainTime"
            ppover = {
                "WabaoRemainTime": {
                    "recognition": "OCR",
                    "expected": "秒",
                    "roi": [230, 240, 190, 190]
                }
            }
            # 等待就绪
            while True:
                print("等待挖宝工具cd中")
                controller.post_screencap().wait
                image = controller.cached_image
                miaoReuslt = context.run_recognition(entry, image, ppover)
                if miaoReuslt is None:
                    break
                else:
                    time.sleep(3)

            box = result.box
            controller.post_click(int(box.x+box.w/2), int(box.y+box.h/2)).wait()
            context.override_next(argv.current_task_name, ["KeyPickupAll"])

        global analyzed
        analyzed = True

        return CustomRecognition.AnalyzeResult(box=(0, 0, 100, 100), detail="")

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
    
class WaitAct(CustomAction):
    def run(self, context: Context, argv: CustomAction.RunArg) -> CustomAction.RunResult:
        print(
            "on WaitAct.run"
        )
        controller = context.tasker.controller
        # 尝试上马
        time.sleep(2)
        controller.post_press_key(0x00000030).wait()

        action_params = json.loads(argv.custom_action_param)
        sleepTime = float(action_params["wait_time"])
        time.sleep(sleepTime)

        global runned
        runned = True
        
        return CustomAction.RunResult(success=True)



class MyRecognition(CustomRecognition):

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        print(
            f"on MyRecognition.analyze, context: {context}, image: {argv.image.shape}, task_detail: {argv.task_detail}, reco_name: {argv.custom_recognition_name}, reco_param: {argv.custom_recognition_param}"
        )
        entry = "ColorMatch"
        ppover = {
            "ColorMatch": {
                "recognition": "ColorMatch",
                "lower": [100, 100, 100],
                "upper": [255, 255, 255],
                "action": "Click",
            }
        }
        context.run_pipeline(entry, ppover)
        context.run_action(entry, [114, 514, 191, 810], "RunAction Detail", ppover)
        reco_detail = context.run_recognition(entry, argv.image, ppover)

        print(f"reco_detail: {reco_detail}")

        new_ctx = context.clone()
        new_ctx.override_pipeline({"TaskA": {}, "TaskB": {}})
        new_ctx.override_next(argv.current_task_name, ["TaskA", "TaskB"])

        node_detail = new_ctx.tasker.get_latest_node("ColorMatch")
        print(node_detail)

        task_job = new_ctx.get_task_job()
        new_task_detail = task_job.get()
        print(new_task_detail)

        global analyzed
        analyzed = True

        return CustomRecognition.AnalyzeResult(
            box=(11, 4, 5, 14), detail="Hello World!"
        )


class MyAction(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        print(
            f"on MyAction.run, context: {context}, task_detail: {argv.task_detail}, action_name: {argv.custom_action_name}, action_param: {argv.custom_action_param}, box: {argv.box}, reco_detail: {argv.reco_detail}"
        )
        controller = context.tasker.controller
        new_image = controller.post_screencap().wait().get()
        print(f"new_image: {new_image.shape}")
        controller.post_click(191, 98).wait()
        controller.post_swipe(100, 200, 300, 400, 100).wait()
        controller.post_input_text("Hello World!").wait()
        controller.post_press_key(32).wait()
        controller.post_touch_down(1, 100, 100, 0).wait()
        controller.post_touch_move(1, 200, 200, 0).wait()
        controller.post_touch_up(1).wait()
        controller.post_start_app("aaa")
        controller.post_stop_app("bbb")

        cached_image = controller.cached_image
        connected = controller.connected
        uuid = controller.uuid
        controller.set_screenshot_target_long_side(1080)
        controller.set_screenshot_target_short_side(720)

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