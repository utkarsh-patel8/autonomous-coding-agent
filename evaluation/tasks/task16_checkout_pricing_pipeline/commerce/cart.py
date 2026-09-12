from dataclasses import dataclass, field
from .models import CartLine


@dataclass
class Cart:
    lines: list[CartLine] = field(default_factory=list)

    def add(self, line: CartLine) -> None:
        self.lines.append(line)

    @property
    def subtotal_cents(self) -> int:
        return sum(line.subtotal_cents for line in self.lines)
