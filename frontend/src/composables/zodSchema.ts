import type { TypedSchema, TypedSchemaError } from "vee-validate";
import type { z } from "zod";

/**
 * Custom schema bridge connecting Zod v4 with VeeValidate.
 *
 * Provides a lightweight bridge between Zod v4 and VeeValidate:
 * 1. VeeValidate passes form values to parse()
 * 2. Zod executes safeParse() and returns success or error issues
 * 3. Zod error issues are formatted into VeeValidate error objects
 */
export function toTypedSchema<TOutput extends Record<string, unknown>>(
  zodSchema: z.ZodType<TOutput>
): TypedSchema<TOutput> {
  return {
    __type: "VVTypedSchema",

    async parse(values: Record<string, unknown>) {
      const result = zodSchema.safeParse(values);

      if (result.success) {
        return {
          value: result.data as TOutput,
          errors: [],
        };
      }

      // Convert Zod issues to VeeValidate schema errors
      const errors: TypedSchemaError[] = result.error.issues.map((issue) => ({
        path: issue.path.map(String).join(".") || issue.path[0]?.toString(),
        errors: [issue.message],
      }));

      return { errors };
    },
  };
}
