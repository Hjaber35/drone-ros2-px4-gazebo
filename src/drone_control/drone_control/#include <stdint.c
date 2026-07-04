#include <stdint.h>

/* RCC */
#define RCC_APB2ENR (*(volatile uint32_t *)0x40021018)

/* GPIOA */
#define GPIOA_CRL   (*(volatile uint32_t *)0x40010800)
#define GPIOA_ODR   (*(volatile uint32_t *)0x4001080C)

/* GPIOB */
#define GPIOB_CRH   (*(volatile uint32_t *)0x40010C04)
#define GPIOB_IDR   (*(volatile uint32_t *)0x40010C08)
#define GPIOB_ODR   (*(volatile uint32_t *)0x40010C0C)

static void delay_bit(void)
{
    for (volatile uint32_t i = 0; i < 40000; i++)
    {
        __asm volatile ("nop");
    }
}

static void delay_gap(void)
{
    for (volatile uint32_t i = 0; i < 300000; i++)
    {
        __asm volatile ("nop");
    }
}

static void send_state(uint8_t state)
{
    /*
     * TXD high = recessive
     * TXD low  = dominant
     */

    if (state)
    {
        GPIOB_ODR |= (1U << 9);      /* PB9 high */
    }
    else
    {
        GPIOB_ODR &= ~(1U << 9);     /* PB9 low */
    }

    delay_bit();
}

int main(void)
{
    /*
     * Enable GPIOA and GPIOB clocks.
     *
     * Bit 2 = GPIOA
     * Bit 3 = GPIOB
     */
    RCC_APB2ENR |= (1U << 2);
    RCC_APB2ENR |= (1U << 3);

    /*
     * PA0 output push-pull, 2 MHz.
     * Used only as an optional receive indicator.
     */
    GPIOA_CRL &= ~(0xFU << 0);
    GPIOA_CRL |=  (0x2U << 0);

    /*
     * PB8 input with pull-up.
     *
     * PB8 configuration is GPIOB_CRH bits 3:0.
     */
    GPIOB_CRH &= ~(0xFU << 0);
    GPIOB_CRH |=  (0x8U << 0);
    GPIOB_ODR |=  (1U << 8);

    /*
     * PB9 output push-pull, 2 MHz.
     *
     * PB9 configuration is GPIOB_CRH bits 7:4.
     */
    GPIOB_CRH &= ~(0xFU << 4);
    GPIOB_CRH |=  (0x2U << 4);

    /*
     * Start with TXD high.
     * This puts the CAN bus in the recessive state.
     */
    GPIOB_ODR |= (1U << 9);

    while (1)
    {
        /*
         * Send repeating pattern:
         * 1 0 1 1 0 0 1 0
         */

        send_state(1);
        send_state(0);
        send_state(1);
        send_state(1);
        send_state(0);
        send_state(0);
        send_state(1);
        send_state(0);

        /*
         * Return bus to recessive during the gap.
         */
        GPIOB_ODR |= (1U << 9);

        /*
         * Read transceiver RXD on PB8.
         * PA0 follows PB8 so it can also be checked with a scope.
         */
        if (GPIOB_IDR & (1U << 8))
        {
            GPIOA_ODR |= (1U << 0);
        }
        else
        {
            GPIOA_ODR &= ~(1U << 0);
        }

        delay_gap();
    }
}