import { Client, ChannelType, TextChannel, ForumChannel, Guild } from 'discord.js';

/**
 * Resolves a channel name to its ID in a given guild.
 * Returns the channel ID if found, otherwise null.
 */
export async function getChannelIdByName(client: Client, guildId: string, channelName: string): Promise<string | null> {
  const guild = await client.guilds.fetch(guildId);
  if (!guild) return null;
  const channels = await guild.channels.fetch();
  for (const [, channel] of channels) {
    if (channel && channel.name === channelName) {
      return channel.id;
    }
  }
  return null;
}

/**
 * Resolves multiple channel names to their IDs in a given guild.
 * Returns an array of channel IDs (skips names not found).
 */
export async function getChannelIdsByNames(client: Client, guildId: string, channelNames: string[]): Promise<string[]> {
  const guild = await client.guilds.fetch(guildId);
  if (!guild) return [];
  const channels = await guild.channels.fetch();
  const ids: string[] = [];
  for (const name of channelNames) {
    for (const [, channel] of channels) {
      if (channel && channel.name === name) {
        ids.push(channel.id);
        break;
      }
    }
  }
  return ids;
}
