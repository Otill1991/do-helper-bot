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
    step = int(data.get('step', [1])[0])
    pattern = data.get('pattern', None)  # Get pattern from callback data
    pattern = pattern[0] if pattern is not None else None  # Convert to string if exists
    account = AccountsDB().get(doc_id=doc_id)
    t = '<b>删除实例</b>\n\n'
    
    if step == 1 and pattern == '':
        # First step: Ask for pattern
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton(
                text='取消',
                callback_data=f'list_droplets?doc_id={doc_id}'
            )
        )
        
        bot.edit_message_text(
            text=f'{t}请输入要删除的实例名称模式\n'
                 f'支持模糊匹配，例如输入 "test" 将删除所有名称中包含 "test" 的实例\n'
                 f'直接发送要匹配的名称即可',
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            parse_mode='HTML',
            reply_markup=markup
        )
        return
    
    if step < 3:
        remaining_clicks = 3 - step
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton(
                text=f'确认删除 (还需点击 {remaining_clicks} 次)',
                callback_data=f'delete_account_droplets?doc_id={doc_id}&step={step + 1}&pattern={pattern if pattern is not None else ""}'
            )
        )
        markup.row(
            InlineKeyboardButton(
                text='取消',
                callback_data=f'list_droplets?doc_id={doc_id}'
            )
        )
        
        pattern_text = f'匹配模式: {pattern}\n' if pattern else ''
        delete_type = '匹配的' if pattern else '所有'
        bot.edit_message_text(
            text=f'{t}⚠️ 危险操作 ⚠️\n'
                 f'您确定要删除账号 <code>{account["email"]}</code> 的{delete_type}实例吗？\n'
                 f'{pattern_text}'
                 f'此操作不可撤销！\n'
                 f'还需点击 {remaining_clicks} 次以确认。',
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            parse_mode='HTML',
            reply_markup=markup
        )
        return
    
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
            if pattern is None or pattern.lower() in droplet.name.lower():
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

    pattern_text = f'匹配模式: {pattern}\n' if pattern else ''
    delete_type = '匹配的' if pattern else '所有'
    bot.edit_message_text(
        text=f'{t}{pattern_text}'
             f'已删除 {total_deleted} 个{delete_type}实例\n'
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
            )
        )
        markup.row(
            InlineKeyboardButton(
                text='快速创建1核512M',
                callback_data=f'quick_create_droplet?doc_id={account.doc_id}&size=s-1vcpu-512mb-10gb'
            ),
            InlineKeyboardButton(
                text='快速创建1核1G',
                callback_data=f'quick_create_droplet?doc_id={account.doc_id}&size=s-1vcpu-1gb'
            ),
            InlineKeyboardButton(
                text='快速创建2核2G',
                callback_data=f'quick_create_droplet?doc_id={account.doc_id}&size=s-2vcpu-2gb'
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
        )
    )
    markup.row(
        InlineKeyboardButton(
            text='快速创建1核512M',
            callback_data=f'quick_create_droplet?doc_id={account.doc_id}&size=s-1vcpu-512mb-10gb'
        ),
        InlineKeyboardButton(
            text='快速创建1核1G',
            callback_data=f'quick_create_droplet?doc_id={account.doc_id}&size=s-1vcpu-1gb'
        ),
        InlineKeyboardButton(
            text='快速创建2核2G',
            callback_data=f'quick_create_droplet?doc_id={account.doc_id}&size=s-2vcpu-2gb'
        )
    )
    
    markup.row(
        InlineKeyboardButton(
            text='删除所有实例',
            callback_data=f'delete_account_droplets?doc_id={account.doc_id}&step=1'
        )
    )
    
    markup.row(
        InlineKeyboardButton(
            text='按名称删除实例',
            callback_data=f'delete_account_droplets?doc_id={account.doc_id}&step=1&pattern='
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
