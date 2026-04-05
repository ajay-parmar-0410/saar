import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { BriefingSkeleton } from "./briefing-skeleton";

describe("BriefingSkeleton", () => {
  it("renders without crashing", () => {
    const { container } = render(<BriefingSkeleton />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it("renders pulse animation", () => {
    const { container } = render(<BriefingSkeleton />);
    expect(container.querySelector(".animate-pulse")).toBeInTheDocument();
  });

  it("renders skeleton cards", () => {
    const { container } = render(<BriefingSkeleton />);
    const cards = container.querySelectorAll(".rounded-lg.border");
    expect(cards.length).toBeGreaterThan(0);
  });
});
