import { SendMessageSchema } from '../schemas.js';
import { ToolHandler } from './types.js';
import { handleDiscordError } from "../errorHandler.js";
import { getChannelIdsByNames } from '../utils/channelUtils.js';


// Accepts: guildId, channelNames (string or array), message
export const sendMessageHandler: ToolHandler = async (args, { client }) => {
  // Accept both legacy channelId and new guildId/channelNames
  let guildId = args.guildId;
  let channelNames = args.channelNames;
  let message = args.message;

  // Legacy support: if channelId is present, treat as channel name if not a valid Discord ID
  if (args.channelId) {
    // Discord IDs are snowflakes: all digits, usually 17-19 chars
    const isSnowflake = /^[0-9]{17,19}$/.test(args.channelId);
    if (!isSnowflake) {
      // Treat as channel name
      channelNames = args.channelId;
    } else {
      // Treat as ID, try to send directly
      try {
        if (!client.isReady()) {
          return {
            content: [{ type: "text", text: "Discord client not logged in." }],
            isError: true
          };
        }
        const channel = await client.channels.fetch(args.channelId);
        if (channel && channel.isTextBased() && 'send' in channel) {
          await channel.send(message);
          return {
            content: [{ type: "text", text: `Message successfully sent to channel ID: ${args.channelId}` }]
          };
        } else {
          return {
            content: [{ type: "text", text: `This channel type does not support sending messages` }],
            isError: true
          };
        }
      } catch (error) {
        return handleDiscordError(error);
      }
    }
  }

  // New logic: use channelNames and guildId
  try {
    if (!client.isReady()) {
      return {
        content: [{ type: "text", text: "Discord client not logged in." }],
        isError: true
      };
    }
    if (!guildId || !channelNames) {
      return {
        content: [{ type: "text", text: "guildId and channelNames are required if not using channelId." }],
        isError: true
      };
    }
    // Normalize channelNames to array
    const names = Array.isArray(channelNames) ? channelNames : [channelNames];
    const channelIds = await getChannelIdsByNames(client, guildId, names);
    if (channelIds.length === 0) {
      return {
        content: [{ type: "text", text: `No valid channels found for names: ${names.join(", ")}` }],
        isError: true
      };
    }
    let sentCount = 0;
    let errors: string[] = [];
    for (const channelId of channelIds) {
      try {
        const channel = await client.channels.fetch(channelId);
        if (channel && channel.isTextBased() && 'send' in channel) {
          await channel.send(message);
          sentCount++;
        } else {
          errors.push(`Channel ${channelId} is not text-based or cannot send messages.`);
        }
      } catch (err) {
        errors.push(`Failed to send to channel ${channelId}: ${err}`);
      }
    }
    return {
      content: [{ type: "text", text: `Message sent to ${sentCount} channel(s).${errors.length ? ' Errors: ' + errors.join(' | ') : ''}` }],
      isError: errors.length > 0
    };
  } catch (error) {
    return handleDiscordError(error);
  }
};