import createGroupMemberships from '../src/qv_plural';

describe('createGroupMemberships', () => {
  test('creates group memberships correctly', () => {
    const groups = [[0, 1], [1, 2, 3], [0, 3]];

    const result = createGroupMemberships(groups);

    // Verify that the result is as expected
    expect(result).toEqual([[0, 2], [0, 1], [1], [1, 2]]);
  });

  // Add more test cases if needed
});