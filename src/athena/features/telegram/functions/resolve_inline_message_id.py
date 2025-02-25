import base64
import struct

from src.athena.core.system import logger


def decode_telegram_base64(string):
    return base64.urlsafe_b64decode(string + "=" * (len(string) % 4))


def resolve_inline_message_id(inline_message_id):
    decoded_message = decode_telegram_base64(inline_message_id)
    logger.debug(f"Decoded message length: {len(decoded_message)} bytes")
    logger.debug(f"Raw decoded message: {decoded_message}")

    try:
        # Try the original format (24 bytes)
        if len(decoded_message) == 24:
            dc_id, message_id, chat_id, access_hash = struct.unpack(
                "<iiqq", decoded_message
            )
            logger.debug("24 worked")
        # Try 20-byte format
        elif len(decoded_message) == 20:
            dc_id, message_id, msg_id_2, access_hash = struct.unpack(
                "<iiiq", decoded_message
            )
            chat_id = None
            logger.debug("20 worked")
        # Try 16-byte format
        elif len(decoded_message) == 16:
            dc_id, message_id, chat_id = struct.unpack("<iiq", decoded_message)
            logger.debug("16 worked")
            access_hash = None
        else:
            logger.debug(f"Unexpected message length: {len(decoded_message)}")
            logger.debug("Hex:", decoded_message.hex())
            return None

        logger.debug(f"DC ID: {dc_id}")
        logger.debug(f"Message ID: {message_id}")
        if chat_id is not None:
            logger.debug(f"Chat ID: {chat_id}")
        if access_hash is not None:
            logger.debug(f"Access Hash: {access_hash}")

        return dc_id, message_id, chat_id, access_hash

    except struct.error as e:
        logger.debug(f"Failed to unpack message: {e}")
        logger.debug("Hex dump:", decoded_message.hex())
        return None
