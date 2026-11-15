public class Counter {
    private int value;

    public Counter() {
        this.value = 0;
    }

    public void add(int amount) {
        this.value += amount;
    }

    public int getValue() {
        return this.value;
    }
}
