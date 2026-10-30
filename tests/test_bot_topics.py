import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from textual.widgets import Input, Static
from telethon.tl import types

from telegram_tui.app import ALL_MESSAGES, TelegramTui, TopicScreen
from telegram_tui.client import Dialog, ForumTopic, TelegramBackend


class OfflineApp(TelegramTui):
    async def _connect(self):
        pass


def forum_topic(topic_id, title, unread=0):
    return types.ForumTopic(
        id=topic_id, date=None, peer=types.PeerUser(9), title=title, icon_color=0,
        top_message=topic_id, read_inbox_max_id=0, read_outbox_max_id=0,
        unread_count=unread, unread_mentions_count=0, unread_reactions_count=0,
        unread_poll_votes_count=0, from_id=types.PeerUser(9),
        notify_settings=types.PeerNotifySettings(),
    )


class BackendTopicTests(unittest.IsolatedAsyncioTestCase):
    def backend(self):
        backend = object.__new__(TelegramBackend)
        backend.client = AsyncMock()
        return backend

    async def test_topics_lists_live_threads_only(self):
        backend = self.backend()
        backend.client.return_value = SimpleNamespace(topics=[
            forum_topic(10, "Hey", 2), types.ForumTopicDeleted(11), forum_topic(12, "Plans"),
        ])
        topics = await backend.topics(Dialog(9, "Dora", 0, object(), has_topics=True))
        self.assertEqual(topics, [ForumTopic(10, "Hey", 2), ForumTopic(12, "Plans", 0)])

    async def test_create_topic_returns_id_of_topic_create_message(self):
        backend = self.backend()
        created = types.MessageService(
            id=42, peer_id=types.PeerUser(9), date=None,
            action=types.MessageActionTopicCreate(title="Trip", icon_color=0),
        )
        backend.client.return_value = SimpleNamespace(updates=[
            types.UpdateMessageID(id=42, random_id=1), SimpleNamespace(message=created),
        ])
        topic = await backend.create_topic(Dialog(9, "Dora", 0, object()), "  Trip ")
        self.assertEqual(topic, ForumTopic(42, "Trip"))

    async def test_create_topic_rejects_blank_title(self):
        with self.assertRaises(ValueError):
            await self.backend().create_topic(Dialog(9, "Dora", 0, object()), "   ")

    async def test_loads_and_sends_are_scoped_to_the_dialog_topic(self):
        backend = self.backend()
        backend.client.get_messages = AsyncMock(return_value=[])
        backend.client.send_message = AsyncMock()
        backend.client.send_file = AsyncMock()
        entity = object()
        threaded = Dialog(9, "Dora", 0, entity, has_topics=True, topic_id=10, topic_title="Hey")
        await backend.messages(threaded)
        await backend.send_message(threaded, "hi")
        await backend.send_gif(threaded, object())
        self.assertEqual(backend.client.get_messages.await_args.kwargs["reply_to"], 10)
        backend.client.send_message.assert_awaited_once_with(entity, "hi", reply_to=10)
        self.assertEqual(backend.client.send_file.await_args.kwargs["reply_to"], 10)

        await backend.send_message(Dialog(9, "Dora", 0, entity), "hi")
        backend.client.send_message.assert_awaited_with(entity, "hi", reply_to=None)


def topic_backend():
    dora = Dialog(9, "Dora", 0, object(), is_private=True, is_bot=True, has_topics=True)
    return SimpleNamespace(
        dialogs=[dora], send_message=AsyncMock(), messages=AsyncMock(return_value=[]),
        load_dialogs=AsyncMock(return_value=[dora]),
        topics=AsyncMock(return_value=[ForumTopic(10, "Hey", 2), ForumTopic(12, "Plans")]),
        create_topic=AsyncMock(return_value=ForumTopic(42, "Trip")),
    )


class AppTopicTests(unittest.IsolatedAsyncioTestCase):
    async def test_opening_threaded_bot_picks_a_thread_and_sends_into_it(self):
        api = topic_backend()
        app = OfflineApp(api)
        async with app.run_test() as pilot:
            await pilot.pause()
            app._open_dialog(api.dialogs[0])
            await pilot.pause()
            self.assertIsInstance(app.screen, TopicScreen)
            await pilot.press("down", "enter")
            await pilot.pause()
            self.assertEqual((app.selected.topic_id, app.selected.topic_title), (10, "Hey"))
            self.assertIn("Dora › Hey", str(app.query_one("#chat-title", Static).render()))
            self.assertEqual(api.messages.await_args.args[0].topic_id, 10)
            composer = app.query_one("#composer", Input)
            composer.value = "hello thread"
            await pilot.press("enter")
            await pilot.pause()
            self.assertEqual(api.send_message.await_args.args[0].topic_id, 10)

    async def test_all_messages_clears_thread_and_h_reopens_picker(self):
        api = topic_backend()
        app = OfflineApp(api)
        async with app.run_test() as pilot:
            await pilot.pause()
            app._open_dialog(api.dialogs[0])
            await pilot.pause()
            await pilot.press("down", "enter")
            await pilot.pause()
            app.query_one("#dialogs").focus()
            await pilot.press("h")
            await pilot.pause()
            self.assertIsInstance(app.screen, TopicScreen)
            await pilot.press("up", "enter")
            await pilot.pause()
            self.assertIsNone(app.selected.topic_id)
            self.assertEqual(TopicScreen._label(ALL_MESSAGES), "All messages")

    async def test_n_creates_a_thread_and_opens_it(self):
        api = topic_backend()
        app = OfflineApp(api)
        async with app.run_test() as pilot:
            await pilot.pause()
            app._open_dialog(api.dialogs[0])
            await pilot.pause()
            await pilot.press("n", *"Trip", "enter")
            await pilot.pause()
            api.create_topic.assert_awaited_once_with(api.dialogs[0], "Trip")
            self.assertEqual((app.selected.topic_id, app.selected.topic_title), (42, "Trip"))

    async def test_h_on_plain_chat_explains_there_are_no_threads(self):
        api = topic_backend()
        api.dialogs[0].has_topics = False
        app = OfflineApp(api)
        async with app.run_test() as pilot:
            await pilot.pause()
            app._open_dialog(api.dialogs[0])
            await pilot.pause()
            app.query_one("#dialogs").focus()
            await pilot.press("h")
            await pilot.pause()
            self.assertNotIsInstance(app.screen, TopicScreen)
            api.topics.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
