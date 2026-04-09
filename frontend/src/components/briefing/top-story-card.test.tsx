import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { TopStoryCard, parseTopStory } from "./top-story-card";

describe("parseTopStory", () => {
  it("splits title and summary on first colon-space", () => {
    const result = parseTopStory("Big News: Something happened in the world");
    expect(result.title).toBe("Big News");
    expect(result.summary).toBe("Something happened in the world");
  });

  it("uses full string as title if no separator", () => {
    const result = parseTopStory("Just a title with no colon");
    expect(result.title).toBe("Just a title with no colon");
    expect(result.summary).toBe("");
  });

  it("handles empty string", () => {
    const result = parseTopStory("");
    expect(result.title).toBe("");
    expect(result.summary).toBe("");
  });
});

describe("TopStoryCard", () => {
  it("renders title and summary", () => {
    render(<TopStoryCard topStory="Big Headline: A detailed summary here" />);
    expect(screen.getByText("Big Headline")).toBeDefined();
    expect(screen.getByText("A detailed summary here")).toBeDefined();
  });

  it("renders Top Story badge", () => {
    render(<TopStoryCard topStory="Test: Summary" />);
    expect(screen.getByText("Top Story")).toBeDefined();
  });

  it("returns null for empty topStory", () => {
    const { container } = render(<TopStoryCard topStory="" />);
    expect(container.innerHTML).toBe("");
  });
});
