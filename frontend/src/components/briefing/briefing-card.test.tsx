import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BriefingCard } from "./briefing-card";
import type { BriefingItem } from "@/lib/types";

const mockItem: BriefingItem = {
  title: "OpenAI releases GPT-5",
  summary: "Major AI breakthrough announced today.",
  url: "https://example.com/article",
  source: "newsapi",
  impact: "HIGH",
};

describe("BriefingCard", () => {
  it("renders title and summary", () => {
    render(<BriefingCard item={mockItem} />);
    expect(screen.getByText("OpenAI releases GPT-5")).toBeInTheDocument();
    expect(screen.getByText("Major AI breakthrough announced today.")).toBeInTheDocument();
  });

  it("renders source name", () => {
    render(<BriefingCard item={mockItem} />);
    expect(screen.getByText("newsapi")).toBeInTheDocument();
  });

  it("renders impact badge", () => {
    render(<BriefingCard item={mockItem} />);
    expect(screen.getByText("HIGH")).toBeInTheDocument();
  });

  it("links to the article URL", () => {
    render(<BriefingCard item={mockItem} />);
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "https://example.com/article");
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
  });

  it("applies featured styling when featured", () => {
    const { container } = render(<BriefingCard item={mockItem} featured />);
    const link = container.querySelector("a");
    expect(link?.className).toContain("p-5");
  });

  it("applies default styling when not featured", () => {
    const { container } = render(<BriefingCard item={mockItem} />);
    const link = container.querySelector("a");
    expect(link?.className).toContain("p-4");
  });
});
