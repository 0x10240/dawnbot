import asyncio

from core.solvers import AntiCaptchaImageSolver, TwoCaptchaImageSolver, LocalModelImageSolver
from utils import load_config, FileOperations

config = load_config()
captcha_solver = None

if config.captcha_module == "anticaptcha":
    captcha_solver = AntiCaptchaImageSolver(config.anti_captcha_api_key)
elif config.captcha_module == "2captcha":
    captcha_solver = TwoCaptchaImageSolver(config.two_captcha_api_key)
else:
    captcha_solver = LocalModelImageSolver()

file_operations = FileOperations()
semaphore = asyncio.Semaphore(config.threads)
