from pdf.generare_pdf import build_user_report
from aiogram import Router , F
from aiogram.types import Message, FSInputFile
from bd_sqlite.fuction_bd import get_user_by_telegram_id

router = Router()

@router.message(F.text.in_(["📄 Raport PDF", "📄 PDF отчёт"]))
async def generate_report(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    pdf_path = await build_user_report(user.id, user.language)

    texts = {
        "ro": f"📊 Raportul tău este gata!",
        "ru": f"📊 Ваш отчёт готов!"
    }
    
    await message.answer_document(
        document=FSInputFile(pdf_path),
        caption=texts[user.language]
    )
