// Dummy dataset for student assignment streak reminders
export interface Student {
  id: string; // Discord user ID
  name: string;
  assignmentMissing: boolean;
}

export const students: Student[] = [
  {
    id: '123456789012345678', // Replace with actual Discord user ID
    name: 'Alice',
    assignmentMissing: true,
  },
  {
    id: '987654321098765432', // Replace with actual Discord user ID
    name: 'Bob',
    assignmentMissing: false,
  },
];
