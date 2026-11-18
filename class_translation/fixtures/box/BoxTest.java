package org.example;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class BoxTest {
    @Test
    public void testStartsAtZero() {
        Box box = new Box();
        assertEquals(0, box.getValue());
    }

    @org.junit.jupiter.api.Test
    public void testAdd() {
        Box box = new Box();
        box.add(2);
        box.add(3);
        org.junit.jupiter.api.Assertions.assertEquals(5, box.getValue());
    }
}
