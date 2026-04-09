import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { SectionPills } from "./section-pills";

describe("SectionPills", () => {
  const sections = ["All", "Tech & AI", "Markets & Finance", "Science"];

  it("renders all section pills", () => {
    render(
      <SectionPills sections={sections} activeSection="All" onSelect={() => {}} />
    );
    sections.forEach((s) => {
      expect(screen.getByText(s)).toBeDefined();
    });
  });

  it("highlights the active section", () => {
    render(
      <SectionPills sections={sections} activeSection="Tech & AI" onSelect={() => {}} />
    );
    const activeBtn = screen.getByText("Tech & AI");
    expect(activeBtn.className).toContain("bg-primary");
  });

  it("calls onSelect when a pill is clicked", () => {
    const onSelect = vi.fn();
    render(
      <SectionPills sections={sections} activeSection="All" onSelect={onSelect} />
    );
    fireEvent.click(screen.getByText("Markets & Finance"));
    expect(onSelect).toHaveBeenCalledWith("Markets & Finance");
  });
});
