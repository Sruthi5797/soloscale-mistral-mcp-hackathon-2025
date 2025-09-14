import { students } from '../utils/studentDataset.js';
import { ToolContext, ToolResponse } from './types.js';
import { handleDiscordError } from '../errorHandler.js';

/**
 * Sends assignment streak reminders to students who are missing assignments.
 * This should be scheduled to run every 5 minutes.
 */
export async function sendAssignmentReminders(context: ToolContext): Promise<ToolResponse> {
  try {
    if (!context.client.isReady()) {
      return {
        content: [{ type: 'text', text: 'Discord client not logged in.' }],
        isError: true,
      };
    }
    let sentCount = 0;
    let errors: string[] = [];
    for (const student of students) {
      if (student.assignmentMissing) {
        try {
          const user = await context.client.users.fetch(student.id);
          if (user) {
            await user.send(`Hi ${student.name}, you are missing today's assignment! Keep your streak going!`);
            sentCount++;
          } else {
            errors.push(`User not found: ${student.id}`);
          }
        } catch (err) {
          errors.push(`Failed to send DM to ${student.name}: ${err}`);
        }
      }
    }
    return {
      content: [{ type: 'text', text: `Reminders sent to ${sentCount} student(s).${errors.length ? ' Errors: ' + errors.join(' | ') : ''}` }],
      isError: errors.length > 0,
    };
  } catch (error) {
    return handleDiscordError(error);
  }
}
