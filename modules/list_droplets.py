from telebot.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

import digitalocean
from time import sleep

from _bot import bot
from utils.db import AccountsDB
from utils.localizer import localize_region


def delete_account_droplets(call: CallbackQuery, data: dict):
    doc_id = data['doc_id'][0]
    account = AccountsDB().get(doc_id=doc_id)
    t = '<b>删除实例</b>\n\n'
    
    bot.edit_message_text(
        text=f'{t}正在删除实例...\n'
             f'账号: <code>{account["email"]}</code>',
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        parse_mode='HTML'
    )

    total_deleted = 0
    try:
        droplets = digitalocean.Manager(token=account['token']).get_all_droplets()
        for droplet in droplets:
            droplet.destroy()
            total_deleted += 1
    except:
        pass

    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text='刷新列表',
            callback_data=f'list_droplets?doc_id={doc_id}'
        )
    )

    bot.edit_message_text(
        text=f'{t}已删除 {total_deleted} 个实例\n'
             f'账号: <code>{account["email"]}</code>',
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=markup
    )


def list_droplets(call: CallbackQuery, data: dict):
    doc_id = data['doc_id'][0]
    t = '<b>管理实例</b>\n\n'

    account = AccountsDB().get(doc_id=doc_id)

    bot.edit_message_text(
        text=f'{t}'
             f'账号： <code>{account["email"]}</code>\n\n'
             '获取实例中...',
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        parse_mode='HTML'
    )

    droplets = digitalocean.Manager(token=account['token']).get_all_droplets()

    markup = InlineKeyboardMarkup()

    if len(droplets) == 0:
        markup.row(
            InlineKeyboardButton(
                text='创建实例',
                callback_data=f'create_droplet?nf=select_region&doc_id={account.doc_id}'
            ),
            InlineKeyboardButton(
                text='快速创建1核1G',
                callback_data=f'quick_create_droplet?doc_id={account.doc_id}'
            )
        )
        markup.row(
            InlineKeyboardButton(
                text='返回',
                callback_data='manage_droplets'
            ),
            InlineKeyboardButton(
                text='刷新',
                callback_data=f'list_droplets?doc_id={account.doc_id}'
            )
        )

        bot.edit_message_text(
            text=f'{t}'
                 f'账号： <code>{account["email"]}</code>\n\n'
                 '没有实例',
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            parse_mode='HTML',
            reply_markup=markup
        )
        return

    for droplet in droplets:
        markup.row(
            InlineKeyboardButton(
                text=f'{droplet.name} ({localize_region(droplet.region["slug"])}) ({droplet.size_slug})',
                callback_data=f'droplet_detail?doc_id={account.doc_id}&droplet_id={droplet.id}'
            )
        )
    
    markup.row(
        InlineKeyboardButton(
            text='创建实例',
            callback_data=f'create_droplet?nf=select_region&doc_id={account.doc_id}'
        ),
        InlineKeyboardButton(
            text='快速创建1核1G',
            callback_data=f'quick_create_droplet?doc_id={account.doc_id}'
        )
    )
    
    markup.row(
        InlineKeyboardButton(
            text='删除所有实例',
            callback_data=f'delete_account_droplets?doc_id={account.doc_id}'
        )
    )
    
    markup.row(
        InlineKeyboardButton(
            text='返回',
            callback_data='manage_droplets'
        ),
        InlineKeyboardButton(
            text='刷新',
            callback_data=f'list_droplets?doc_id={account.doc_id}'
        )
    )

    bot.edit_message_text(
        text=f'{t}'
             f'账号： <code>{account["email"]}</code>\n\n'
             '请选择实例',
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=markup
    )
