import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

# 文件名
DATA_FILE = "records.csv"
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["时间", "分类", "金额"])
    df.to_csv(DATA_FILE, index=False)

async def record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("用法：/记账 分类 金额\n例如：/记账 吃饭 120")
        return

    category = context.args[0]
    try:
        amount = float(context.args[1])
    except ValueError:
        await update.message.reply_text("金额必须是数字！")
        return

    time = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_data = pd.DataFrame([[time, category, amount]], columns=["时间", "分类", "金额"])
    df_existing = pd.read_csv(DATA_FILE)
    df_combined = pd.concat([df_existing, new_data], ignore_index=True)
    df_combined.to_csv(DATA_FILE, index=False)

    await update.message.reply_text(f"已记账：{category} - {amount}元")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        df_data = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        await update.message.reply_text("还没有任何记录")
        return

    if df_data.empty:
        await update.message.reply_text("账本是空的")
        return

    summary = df_data.groupby("分类")["金额"].sum()
    msg = "分类统计：\n"
    for cat, total in summary.items():
        msg += f"{cat}: {total:.2f} 元\n"

    await update.message.reply_text(msg)

app = ApplicationBuilder().token("7969129288:AAEZ6BoBKB3o493i0ALVJzV9PPwzkA7yZdU").build()
app.add_handler(CommandHandler("record", record))
app.add_handler(CommandHandler("stats", stats))

print("记账机器人正在运行...")
app.run_polling()
