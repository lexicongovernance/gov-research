import createGroupMemberships, { commonGroup } from '../src/qv_plural';

// test create group memberships 
describe('createGroupMemberships', () => {
  test('creates group memberships correctly', () => {
    const groups = [[0, 1], [1, 2, 3], [0, 2]];

    const result = createGroupMemberships(groups);

    // Verify that the result is as expected
    expect(result).toEqual([[0, 2], [0, 1], [1, 2], [1]]);
  });
});

// test common group
describe('commonGroup', () => {
  test('should return true if participants share a common group', () => {
    const groupMemberships: number[][] = [[0, 2], [0, 1], [1, 2], [1]];

    const result = commonGroup(0, 1, groupMemberships);
    expect(result).toBe(true);
  });

  test('should return false if participants do not share a common group', () => {
    const groupMemberships: number[][] = [[0, 2], [0, 1], [1, 2], [1]];

    const result = commonGroup(0, 3, groupMemberships);
    expect(result).toBe(false);
  });
});