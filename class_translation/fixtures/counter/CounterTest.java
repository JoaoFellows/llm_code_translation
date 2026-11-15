import org.junit.Test;
import static org.junit.Assert.assertEquals;

public class CounterTest {
    @Test
    public void testStartsAtZero() {
        Counter counter = new Counter();
        assertEquals(0, counter.getValue());
    }

    @Test
    public void testAdd() {
        Counter counter = new Counter();
        counter.add(2);
        counter.add(3);
        assertEquals(5, counter.getValue());
    }
}
