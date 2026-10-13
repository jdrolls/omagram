"""Regression tests for perform_interactive_login's retry-on-wrong-credential paths.

Before this fix, a mistyped 2FA password or phone code propagated straight
out of perform_interactive_login instead of re-prompting, aborting the
whole `omagram auth` flow.
"""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from telethon.errors import PasswordHashInvalidError, SessionPasswordNeededError

from telegram_tui.cli import perform_interactive_login


def _fake_backend(**client_kwargs) -> SimpleNamespace:
    client = SimpleNamespace(**client_kwargs)
    return SimpleNamespace(client=client, send_code=AsyncMock(), sign_in=AsyncMock())


class PerformInteractiveLoginTests(unittest.IsolatedAsyncioTestCase):
    async def test_retries_after_wrong_2fa_password(self):
        qr_login = SimpleNamespace(url="tg://login?token=x", wait=AsyncMock(side_effect=SessionPasswordNeededError(request=None)))
        sign_in = AsyncMock(side_effect=[PasswordHashInvalidError(request=None), None])
        backend = _fake_backend(qr_login=AsyncMock(return_value=qr_login), sign_in=sign_in)

        with patch("telegram_tui.cli.print_qr"), patch(
            "telegram_tui.cli.getpass.getpass", side_effect=["wrong", "right"]
        ), patch("builtins.print"):
            await perform_interactive_login(backend)

        self.assertEqual(sign_in.await_count, 2)

    async def test_retries_after_wrong_phone_code(self):
        from telethon.errors import PhoneCodeInvalidError

        qr_login = SimpleNamespace(url="tg://login?token=x", wait=AsyncMock(side_effect=RuntimeError("qr failed")))
        backend = _fake_backend(qr_login=AsyncMock(return_value=qr_login))
        backend.sign_in = AsyncMock(side_effect=[PhoneCodeInvalidError(request=None), None])

        with patch("telegram_tui.cli.print_qr"), patch("builtins.print"), patch(
            "telegram_tui.cli.input", side_effect=["p", "+491234", "111111", "222222"]
        ), patch("telegram_tui.cli.getpass.getpass", return_value=""):
            await perform_interactive_login(backend)

        self.assertEqual(backend.sign_in.await_count, 2)
        # send_code is called once up front, then again after an invalid
        # code (perform_interactive_login requests a fresh one).
        self.assertEqual(backend.send_code.await_count, 2)


if __name__ == "__main__":
    unittest.main()
